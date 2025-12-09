from uuid import UUID
import jwt
from datetime import datetime, timedelta, timezone

from app.schemas import schemas
from app.utils.errors import require, Unauthorized, BadRequest
from config import settings

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expiration_date": str(expire)})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        id: UUID = payload.get("id")
        require(id is not None, Unauthorized("Invalid token"))
        expiration_date = payload.get("expiration_date")

        # expiration_date should exist and be in the future
        require(
            expiration_date is not None and datetime.now() <= datetime.fromisoformat(expiration_date),
            Unauthorized("Token expired or invalid"))

        token_data = schemas.TokenData(id=id, expiration_date=expiration_date)
        return token_data
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token")


def get_token(token: str):
    try:
        token_type, tok = str.split(token, sep=" ")
    except Exception:
        raise BadRequest("Invalid Authorization header format")

    require(token_type.lower() == "bearer", Unauthorized("Could not validate credentials"))
    require(tok, Unauthorized("Invalid token"))
    return tok
