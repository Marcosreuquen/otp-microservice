from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.models.db import get_session
from app.controllers import authServiceController
from app.lib.otp import generate_otp, verify_otp
from app.schemas import schemas

router = APIRouter(prefix="/code", tags=["code"])

@router.get("/generate/{app_id}")
async def generate_mfa(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    secret = authServiceController.get_secret(user_id, app_id, session)

    if not secret:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    otp = generate_otp(secret)

    return otp

@router.get("/sms")
async def send_sms_mfa():
    return {}

@router.get("/email")
async def send_email_mfa():
    return {}

@router.post("/verify")
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