from fastapi import HTTPException, status
from uuid import UUID
from sqlmodel import Session, select

from app.models.tables import AuthService
from app.utils.otp import generate_secret
from app.utils.schemas import MFARegister, RecoveryMFAData


def register_mfa(user_id: UUID, data: MFARegister, session: Session):
    record = AuthService(
        user_id=user_id,
        app_id=data.app_id,
        recovery_method=data.recovery_method,
        otp_method=data.otp_method,
        otp_secret=generate_secret(),
        enabled= True
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    return record

def disable_mfa(user_id: UUID,app_id: UUID, session: Session):
    statement = select(AuthService).where(AuthService.user_id == user_id)
    record = session.exec(statement).first()

    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    if not record.enabled:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Record already disabled")

    record.enabled = False
    session.add(record)
    session.commit()
    session.refresh(record)
    succeed = record.enabled == False
    return succeed

def enable_mfa(user_id: UUID, app_id: UUID, session: Session):
    statement = select(AuthService).where(AuthService.user_id == user_id, AuthService.app_id == app_id)
    record = session.exec(statement).first()

    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.enabled:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Record already enabled")

    record.enabled = True
    session.add(record)
    session.commit()
    session.refresh(record)
    succeed = record.enabled == True
    return succeed


def status_mfa(user_id: UUID, app_id: UUID, session: Session):
    statement = select(AuthService).where(AuthService.user_id == user_id, AuthService.app_id == app_id)
    record = session.exec(statement).first()

    if record and record.enabled:
        return True
    return False

def recovery_mfa(user_id: UUID, body: RecoveryMFAData, session: Session):
    statement = select(AuthService).where(AuthService.user_id == user_id, AuthService.app_id == body.app_id)
    record = session.exec(statement).first()

    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    if not record.otp_method == body.otp_method:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Invalid OTP method")

    record.recovery_method = body.recovery_method
    record.otp_method = body.otp_method
    record.otp_secret = generate_secret()
    session.add(record)
    session.commit()
    session.refresh(record)
    succeed = record.recovery_method == body.recovery_method and record.otp_method == body.otp_method
    return succeed