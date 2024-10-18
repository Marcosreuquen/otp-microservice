from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.controllers.authServiceController import get_service_with_user_and_app
from app.lib.twilio import send_sms, send_whatsapp
from app.models.db import get_session
from app.controllers import authServiceController, userController, appController
from app.lib.otp import generate_otp, verify_otp
from app.schemas import schemas
from app.utils.decorators import RequiresAuthentication

router = APIRouter(prefix="/code", tags=["code"])

@router.get("/generate/{app_id}")
@RequiresAuthentication
async def generate_mfa(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    secret = authServiceController.get_secret(user_id, app_id, session)

    if not secret:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    otp = generate_otp(secret)

    return {"code": otp}

@router.post("/sms")
@RequiresAuthentication
async def send_sms_mfa(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret

    if not secret:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    otp = generate_otp(secret)

    if not otp:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error generating OTP")

    phone_number = service.User.phone_number

    if not phone_number:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Phone number not found")

    app_name = service.App.name

    if not app_name:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not found")

    message = send_sms(
        to=phone_number,
        body=f"Your verification code for {app_name} is: {otp}"
    )

    if not message:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error sending SMS")

    return {"success": True}

@router.post("/whatsapp")
@RequiresAuthentication
async def send_whatsapp_mfa(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret

    if not secret:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    otp = generate_otp(secret)

    if not otp:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error generating OTP")
    phone_number = service.User.phone_number

    if not phone_number:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Phone number not found")

    message = send_whatsapp(
        to=phone_number,
        code=otp
    )

    if not message:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error sending SMS")

    return {"success": True}


@router.get("/email")
@RequiresAuthentication
async def send_email_mfa(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    service = get_service_with_user_and_app(user_id, app_id, session)

    secret = service.AuthService.secret
    if not secret:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    otp = generate_otp(secret)

    if not otp:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error generating OTP")
    email = service.User.email

    if not email:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Email not found")

    app_name = service.App.name

    if not app_name:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not found")

    response = send_sms(
        to=email,
        body=f"Your verification code for {app_name} is: {otp}"
    )

    if not response:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error sending email")
    return {"success": True}

@router.post("/verify")
@RequiresAuthentication
async def verify_mfa( body: schemas.VerifyOTP, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id
    otp = body.otp

    if not user_id or not app_id or not otp:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    secret = authServiceController.get_secret(user_id, app_id, session)
    if not secret:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    result = verify_otp(secret, otp)

    if not result:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")

    return {"success": True}