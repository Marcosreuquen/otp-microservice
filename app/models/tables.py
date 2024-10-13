from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, UTC, timedelta
import uuid
from uuid import UUID

class UserAppLink(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    app_id: UUID = Field(foreign_key="app.id", primary_key=True)


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    username: str = Field(index=True, max_length=50, default=None, unique=True)
    email: str = Field(index=True, unique=True, max_length=100)
    auth_services: List["AuthService"] = Relationship(back_populates="user")
    apps: List["App"] = Relationship(back_populates="users", link_model=UserAppLink)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))


class AuthService(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="auth_services")
    app_id: UUID = Field(foreign_key="app.id")
    recovery_method: str = Field(max_length=50)
    otp_method: str = Field(max_length=50)
    otp_secret: str = Field(max_length=100)
    enabled: bool = Field(default=False, index=True)
    expiration_date: Optional[datetime]
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

class App(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    name: str = Field(index=True, max_length=100)
    api_key_secret: str = Field(index=True, max_length=256)
    users: List["User"] = Relationship(back_populates="apps", link_model=UserAppLink)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

class Auth(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", unique=True, index=True)
    password_hash: Optional[str] = Field(max_length=256)
    token_type: Optional[str] = Field(default="bearer", nullable=False)
    expires_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC) + timedelta(days=90))
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))
