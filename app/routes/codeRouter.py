from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from uuid import UUID

from app.controllers.authServiceController import get_service_with_user_and_app
from app.lib.twilio import send_sms, send_whatsapp
from app.lib.resend import send_email, get_template
from app.models.db import get_session
from app.controllers import authServiceController
from app.lib.otp import generate_otp, verify_otp
from app.schemas import schemas
from app.utils.decorators import RequiresAuthentication
from app.utils.exceptionHandler import ExceptionService

router = APIRouter(prefix="/code", tags=["code"])

@router.get("/generate/{app_id}")
@RequiresAuthentication
async def generate_otp(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    secret = authServiceController.get_secret(user_id, app_id, session)
    ExceptionService.handle(secret, 404, "User not found")

    otp = generate_otp(secret)

    return {"code": otp}

@router.post("/sms")
@RequiresAuthentication
async def send_sms_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret
    ExceptionService.handle(secret, 404, "User not found")
    otp = generate_otp(secret)
    ExceptionService.handle(otp, 500, "Error generating OTP")
    phone_number = service.User.phone_number
    ExceptionService.handle(phone_number, 404, "Phone number not found")
    app_name = service.App.name
    ExceptionService.handle(app_name, 404, "App not found")

    message = send_sms(
        to=phone_number,
        body=f"Your verification code for {app_name} is: {otp}"
    )
    ExceptionService.handle(message, 500, "Error sending SMS")

    return {"success": True}

@router.post("/whatsapp")
@RequiresAuthentication
async def send_whatsapp_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    ExceptionService.handle(user_id and app_id, 401)
    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret
    ExceptionService.handle(secret, 404, "User not found")
    otp = generate_otp(secret)
    ExceptionService.handle(otp, 500, "Error generating OTP")
    phone_number = service.User.phone_number
    ExceptionService.handle(phone_number, 404, "Phone number not found")
    message = send_whatsapp(
        to=phone_number,
        code=otp
    )
    ExceptionService.handle(message, 500, "Error sending WhatsApp message")

    return {"success": True}


@router.get("/email")
@RequiresAuthentication
async def send_email_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    ExceptionService.handle(user_id and app_id, 401)
    service = get_service_with_user_and_app(user_id, app_id, session)
    secret = service.AuthService.secret
    ExceptionService.handle(secret, 404, "User not found")
    otp = generate_otp(secret)
    ExceptionService.handle(otp, 500, "Error generating OTP")
    email = service.User.email
    ExceptionService.handle(email, 404, "Email not found")
    app_name = service.App.name
    ExceptionService.handle(app_name, 404, "App not found")

    response = send_email(
        to=email,
        subject=f"Your verification code for {app_name}",
        body=get_template(app_name, otp)
        
    )
    ExceptionService.handle(response, 500, "Error sending email")

    return {"success": True}

@router.post("/verify")
@RequiresAuthentication
async def verify_otp( body: schemas.VerifyOTP, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id
    otp = body.otp

    ExceptionService.handle(user_id and app_id and otp, 401)
    secret = authServiceController.get_secret(user_id, app_id, session)
    ExceptionService.handle(secret, 404, "User not found")
    result = verify_otp(secret, otp)
    ExceptionService.handle(result, 401, "Invalid OTP")


    return {"success": True}