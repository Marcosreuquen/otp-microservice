from fastapi import HTTPException, status
from ..models.tables import App
from sqlmodel import Session, select
from uuid import UUID

from app.lib.otp import generate_secret


def create_app(user_id: UUID, name: str, session: Session):
    statement = select(App).where(App.owner_id == user_id, App.name == name)
    record = session.exec(statement).first()
    if record:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Record already exists")
    record = App(
        name=name,
        owner_id=user_id,
        api_key_secret=generate_secret()
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_app_by_id(app_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()
    return record

def get_app_by_name(name: str, session: Session):
    statement = select(App).where(App.name == name)
    record = session.exec(statement).first()
    return record

def update_app_name(user_id: UUID, app_id: UUID, name: str, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.owner_id != user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    record.name = name
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def delete_app(user_id: UUID, app_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")

    if record.owner_id != user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    session.delete(record)
    session.commit()
    return record

def reset_api_key_secret(app_id: UUID, user_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()

    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.owner_id != user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    record.api_key_secret = generate_secret()
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

def get_api_key_secret(app_id: UUID, user_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id, App.owner_id == user_id)
    record = session.exec(statement).first()
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record

def get_user_apps(user_id: UUID, app_id: UUID, session: Session):
    statement = select(App).where(App.owner_id == user_id, App.id == app_id)
    records = session.exec(statement).all()
    return records

def add_user_to_app(user_id: UUID, app_id: UUID, session: Session):
    # it's not the logic we need.
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.owner_id != user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    record.users.append(user_id)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record
