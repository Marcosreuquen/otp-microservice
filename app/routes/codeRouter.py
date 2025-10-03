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
async def send_sms_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

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
async def send_whatsapp_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    require(user_id and app_id, Unauthorized("Unauthorized"))
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
async def send_email_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    require(user_id and app_id, Unauthorized("Unauthorized"))
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
async def verify_code( body: schemas.VerifyOTP, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id
    otp = body.otp

    require(user_id and app_id and otp, Unauthorized("Unauthorized"))
    secret = authServiceController.get_secret(user_id, app_id, session)
    require(secret, NotFound("User not found"))
    result = verify_otp(secret, otp)
    require(result, Unauthorized("Invalid OTP"))


    return {"success": True}