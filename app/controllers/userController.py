from sqlmodel import Session, select
from uuid import UUID

from app.models.tables import User
from app.schemas import schemas


def get_user(username: str, session: Session) -> User | None:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user

def user_exists(username: str, session: Session) -> bool:
    user = get_user(username, session)
    return bool(user)

def create_user(user: schemas.CreateUser, session: Session) :
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_id(user_id: UUID, session: Session) -> User | None:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user