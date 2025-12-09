from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from uuid import UUID

from app.schemas.enums import RecoveryMethod, OtpMethod


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    username: str = Field(index=True, max_length=50, default=None, unique=True)
    email: str = Field(index=True, unique=True, max_length=100)
    phone_number: Optional[str] = Field(max_length=20, default=None)
    auth_services: List["AuthService"] = Relationship(back_populates="user")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class App(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    name: str = Field(index=True, max_length=100)
    api_key_secret: str = Field(index=True, max_length=256)
    owner_id: UUID = Field(foreign_key="user.id", unique=True)
    auth_services: List["AuthService"] = Relationship(back_populates="app")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class AuthService(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    app_id: UUID = Field(foreign_key="app.id", index=True)
    recovery_method: RecoveryMethod = Field(max_length=50)
    otp_method: OtpMethod = Field(max_length=50)
    otp_secret: str = Field(max_length=100)
    enabled: bool = Field(default=False, index=True)
    user: Optional[User] = Relationship(back_populates="auth_services")
    app: Optional[App] = Relationship(back_populates="auth_services")
    expiration_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=365))
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class Auth(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", unique=True, index=True)
    password_hash: Optional[str] = Field(max_length=256)
    token_type: Optional[str] = Field(default="bearer", nullable=False)
    expires_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=90))
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
