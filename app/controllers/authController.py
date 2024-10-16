from sqlmodel import Session, select
from datetime import datetime, timedelta, UTC
from uuid import UUID

from app.models.tables import Auth, User

def create_auth_record(user: User, password_hash: str, session: Session):
    auth_record = Auth(
        user_id=user.id,
        password_hash=password_hash,
        token_type="bearer",
        expires_at=datetime.now(UTC) + timedelta(days=30))

    session.add(auth_record)
    session.commit()
    session.refresh(auth_record)
    if auth_record:
        return True

    return False

def get_auth_record(user_id: UUID, session: Session):
    statement = select(Auth).where(Auth.user_id == user_id)
    auth_record = session.exec(statement).first()
    return auth_record
