from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

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