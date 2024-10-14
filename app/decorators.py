from fastapi import Request, Response, HTTPException, status
from functools import wraps

from app.utils.oauth import get_token, verify_access_token


def RequiresAuthentication(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header not found"
            )
        token = get_token(auth_header)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not found"
            )
        try:
            credential_exceptions = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            data = verify_access_token(token, credential_exceptions)
            request.state.user_id = data.id
        finally:
            pass

        return await func(*args, **kwargs)
    return wrapper
