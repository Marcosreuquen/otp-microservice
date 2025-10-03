from ..models.tables import App
from sqlmodel import Session, select
from uuid import UUID

from app.lib.otp import generate_secret
from ..utils.errors import require, NotFound, Conflict, Unauthorized


def create_app(user_id: UUID, name: str, session: Session):
    statement = select(App).where(App.owner_id == user_id, App.name == name)
    record = session.exec(statement).first()
    # Ensure there is no existing app with same owner and name
    require(not record, Conflict("Record already exists"))

    record = App(
        name=name,
        owner_id=user_id,
        api_key_secret=f"OTP-{name.lower().replace(' ', '_')}-{generate_secret()}"
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

    require(record, NotFound("Record not found"))
    require(record.owner_id == user_id, Unauthorized("Unauthorized"))

    record.name = name
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def delete_app(user_id: UUID, app_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()

    require(record, NotFound("Record not found"))
    require(record.owner_id == user_id, Unauthorized("Unauthorized"))

    session.delete(record)
    session.commit()
    return record


def reset_api_key_secret(app_id: UUID, user_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id)
    record = session.exec(statement).first()

    require(record, NotFound("Record not found"))
    require(record.owner_id == user_id, Unauthorized("Unauthorized"))

    # Use record.name (not an undefined `name`) when creating the secret
    record.api_key_secret = f"OTP-{record.name.lower().replace(' ', '_')}-{generate_secret()}"
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_api_key_secret(app_id: UUID, user_id: UUID, session: Session):
    statement = select(App).where(App.id == app_id, App.owner_id == user_id)
    record = session.exec(statement).first()
    require(record, NotFound("Record not found"))

    return record


def get_user_apps(user_id: UUID, app_id: UUID, session: Session):
    statement = select(App).where(App.owner_id == user_id, App.id == app_id)
    records = session.exec(statement).all()
    return records