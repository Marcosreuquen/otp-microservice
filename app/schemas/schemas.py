from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.schemas.enums import OtpMethod, RecoveryMethod


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[UUID]
    expiration_date: Optional[datetime]

class UserCredentials(BaseModel):
    username: str
    password: str

class MFARegister(BaseModel):
    app_id: UUID
    user_id: UUID
    username: str
    otp_method: OtpMethod
    recovery_method: RecoveryMethod

class BodyWithAppId(BaseModel):
    app_id: UUID

class RecoveryMFAData(BaseModel):
    app_id: UUID
    recovery_method: RecoveryMethod
    otp_method: OtpMethod

class CreateApp(BaseModel):
    name: str

class UpdateApp(BaseModel):
    name: str

class VerifyOTP(BaseModel):
    otp: str
    app_id: UUID

class BodyWithUri(BaseModel):
    uri: str
