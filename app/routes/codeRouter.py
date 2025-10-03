from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.controllers.authServiceController import get_service_with_user_and_app
from app.lib.twilio import send_sms, send_whatsapp
from app.lib.resend import send_email, get_template
from app.models.db import get_session
from app.controllers import authServiceController
from app.lib.otp import generate_otp as generate_otp_code, verify_otp
from app.schemas import schemas
from app.utils.decorators import RequiresAuthentication
from app.utils.errors import require, NotFound, Unauthorized, InternalError
from app.lib.cache import get_redis
from app.lib.redis_service import redis_service

router = APIRouter(prefix="/code", tags=["code"])

@router.get("/generate/{app_id}")
@RequiresAuthentication
async def generate_code(app_id: UUID, request: Request, session: Session = Depends(get_session), redis = Depends(get_redis)):
    user_id = request.state.user_id
    secret = authServiceController.get_secret(user_id, app_id, session)
    require(secret, NotFound("User not found"))

    # Rate limit: max 5 requests per minute per user+app
    rate_key = f"rate:{user_id}:{app_id}"
    try:
        current = await redis.incr(rate_key)
        if current == 1:
            await redis.expire(rate_key, 60)
    except Exception:
        # If redis fails, don't completely block - fall back to permissive mode
        current = 1

    if current > 5:
        raise HTTPException(status_code=429, detail="Too many requests")

    otp = generate_otp_code(secret)

    # store OTP in redis for short-lived verification (120 seconds)
    otp_key = f"otp:{user_id}:{app_id}"
    try:
        await redis.setex(otp_key, 120, otp)
    except Exception:
        # ignore cache set errors - OTP still returned but not stored
        pass

    return {"code": otp}

@router.post("/sms")
@RequiresAuthentication
async def send_sms_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session), redis = Depends(get_redis)):
    user_id = request.state.user_id
    app_id = body.app_id

    # Rate limiting for SMS sending - max 3 per minute per user+app
    sms_rate_key = f"sms_rate:{user_id}:{app_id}"
    try:
        current = await redis.incr(sms_rate_key)
        if current == 1:
            await redis.expire(sms_rate_key, 60)
        if current > 3:
            raise HTTPException(status_code=429, detail="Too many SMS requests")
    except Exception:
        # If redis fails, continue without rate limiting
        pass

    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret
    require(secret, NotFound("User not found"))
    otp = generate_otp_code(secret)
    require(otp, InternalError("Error generating OTP"))
    phone_number = service.User.phone_number
    require(phone_number, NotFound("Phone number not found"))
    app_name = service.App.name
    require(app_name, NotFound("App not found"))

    message = send_sms(
        to=phone_number,
        body=f"Your verification code for {app_name} is: {otp}"
    )
    require(message, InternalError("Error sending SMS"))

    return {"success": True}

@router.post("/whatsapp")
@RequiresAuthentication
async def send_whatsapp_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session), redis = Depends(get_redis)):
    user_id = request.state.user_id
    app_id = body.app_id

    require(user_id and app_id, Unauthorized("Unauthorized"))
    
    # Rate limiting for WhatsApp sending - max 3 per minute per user+app
    whatsapp_rate_key = f"whatsapp_rate:{user_id}:{app_id}"
    try:
        current = await redis.incr(whatsapp_rate_key)
        if current == 1:
            await redis.expire(whatsapp_rate_key, 60)
        if current > 3:
            raise HTTPException(status_code=429, detail="Too many WhatsApp requests")
    except Exception:
        # If redis fails, continue without rate limiting
        pass
    
    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret
    require(secret, NotFound("User not found"))
    otp = generate_otp_code(secret)
    require(otp, InternalError("Error generating OTP"))
    phone_number = service.User.phone_number
    require(phone_number, NotFound("Phone number not found"))
    message = send_whatsapp(
        to=phone_number,
        code=otp
    )
    require(message, InternalError("Error sending WhatsApp message"))

    return {"success": True}


@router.post("/email")
@RequiresAuthentication
async def send_email_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session), redis = Depends(get_redis)):
    user_id = request.state.user_id
    app_id = body.app_id

    require(user_id and app_id, Unauthorized("Unauthorized"))
    
    # Rate limiting for email sending - max 5 per minute per user+app
    email_rate_key = f"email_rate:{user_id}:{app_id}"
    try:
        current = await redis.incr(email_rate_key)
        if current == 1:
            await redis.expire(email_rate_key, 60)
        if current > 5:
            raise HTTPException(status_code=429, detail="Too many email requests")
    except Exception:
        # If redis fails, continue without rate limiting
        pass
    
    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret
    require(secret, NotFound("User not found"))
    otp = generate_otp_code(secret)
    require(otp, InternalError("Error generating OTP"))
    email = service.User.email
    require(email, NotFound("Email not found"))
    app_name = service.App.name
    require(app_name, NotFound("App not found"))

    response = send_email(
        to=email,
        subject=f"Your verification code for {app_name}",
        body=get_template(app_name, otp)
        
    )
    require(response, InternalError("Error sending email"))

    return {"success": True}

@router.post("/verify")
@RequiresAuthentication
async def verify_code( body: schemas.VerifyOTP, request: Request, session: Session = Depends(get_session), redis = Depends(get_redis)):
    user_id = request.state.user_id
    app_id = body.app_id
    otp = body.otp

    require(user_id and app_id and otp, Unauthorized("Unauthorized"))
    
    # Rate limiting for verification attempts - max 10 per minute per user+app
    verify_rate_key = f"verify_rate:{user_id}:{app_id}"
    try:
        current = await redis.incr(verify_rate_key)
        if current == 1:
            await redis.expire(verify_rate_key, 60)
        if current > 10:
            raise HTTPException(status_code=429, detail="Too many verification attempts")
    except Exception:
        # If redis fails, continue without rate limiting
        pass
    
    # Check if OTP was generated and stored in cache
    otp_key = f"otp:{user_id}:{app_id}"
    cached_otp = None
    try:
        cached_otp = await redis.get(otp_key)
    except Exception:
        # If redis fails, fall back to TOTP verification
        pass
    
    # Verify against cached OTP first (if available), then fall back to TOTP
    if cached_otp and cached_otp == otp:
        # Valid cached OTP - remove it to prevent reuse
        try:
            await redis.delete(otp_key)
        except Exception:
            pass
        return {"success": True}
    
    # Fall back to TOTP verification
    secret = authServiceController.get_secret(user_id, app_id, session)
    require(secret, NotFound("User not found"))
    result = verify_otp(secret, otp)
    require(result, Unauthorized("Invalid OTP"))

    return {"success": True}