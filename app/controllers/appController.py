from ..models.tables import App
from sqlmodel import Session, select
from uuid import UUID

from app.lib.otp import generate_secret
from ..utils.exceptionHandler import ExceptionService


def create_app(user_id: UUID, name: str, session: Session):
    statement = select(App).where(App.owner_id == user_id, App.name == name)
    record = session.exec(statement).first()
    ExceptionService.handle(not record, 409, "Record already exists")
    record = App(
        name=name,
        owner_id=user_id,
        api_key_secret=f"MFA-{name.lower().replace(' ', '_')}-{generate_secret()}"
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

    ExceptionService.handle(record, 404, "Record not found")
    ExceptionService.handle(record.owner_id == user_id, 401, "Unauthorized")

    record.name = name
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def delete_app(user_id: UUID, app_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()

    ExceptionService.handle(record, 404, "Record not found")
    ExceptionService.handle(record.owner_id == user_id, 401, "Unauthorized")

    session.delete(record)
    session.commit()
    return record

def reset_api_key_secret(app_id: UUID, user_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()

    ExceptionService.handle(record, 404, "Record not found")
    ExceptionService.handle(record.owner_id == user_id, 401, "Unauthorized")

    record.api_key_secret = f"MFA-{name.lower().replace(' ', '_')}-{generate_secret()}"
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

def get_api_key_secret(app_id: UUID, user_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id, App.owner_id == user_id)
    record = session.exec(statement).first()
    ExceptionService.handle(record, 404, "Record not found")

    return record

def get_user_apps(user_id: UUID, app_id: UUID, session: Session):
    statement = select(App).where(App.owner_id == user_id, App.id == app_id)
    records = session.exec(statement).all()
    return records