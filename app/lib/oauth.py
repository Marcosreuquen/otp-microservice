from uuid import UUID
from fastapi import status, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC

from app.schemas import schemas
from config import settings

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expiration_date": str(expire)})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str, credentials_exceptions):
    try:
        payload = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        id: UUID = payload.get("id")

        if id is None:
            raise credentials_exceptions

        expiration_date = payload.get("expiration_date")

        if expiration_date is None:
            raise credentials_exceptions

        if datetime.now() > datetime.fromisoformat(expiration_date):
            raise credentials_exceptions

        token_data = schemas.TokenData(id=id, expiration_date=expiration_date)
    except JWTError:
        raise credentials_exceptions
    return token_data


def get_token(token:str):
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    [token_type, token] = str.split(token, sep=" ")

    if not token or token_type.lower() != "bearer":
        raise credentials_exceptions

    return token
