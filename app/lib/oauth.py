from uuid import UUID
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC

from app.schemas import schemas
from app.utils.exceptionHandler import ExceptionService
from config import settings

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expiration_date": str(expire)})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        id: UUID = payload.get("id")
        ExceptionService.handle(id, 401, "Invalid token")
        expiration_date = payload.get("expiration_date")

        ExceptionService.handle(
            expiration_date and datetime.now() > datetime.fromisoformat(expiration_date),
            401,
            "Invalid token")

        token_data = schemas.TokenData(id=id, expiration_date=expiration_date)
    except JWTError:
        ExceptionService.handle(False, 401, "Invalid token")
    return token_data


def get_token(token:str):
    [token_type, token] = str.split(token, sep=" ")
    ExceptionService.handle(token_type.lower() != "bearer", 401, "Could not validate credentials")
    ExceptionService.handle(token, 401, "Invalid token")
    return token
