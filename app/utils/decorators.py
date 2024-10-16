from fastapi import Request, HTTPException, status, Header
from functools import wraps
from typing import Annotated, Callable, Awaitable, Any

from app.lib.oauth import get_token, verify_access_token


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

def TestDecorator(func: Callable[[str, ...], Awaitable[Any]]) -> Callable[[str, ...], Awaitable[Any]]:
    @wraps(func)
    async def wrapper(*args, authorization: Annotated[str, Header()]=None, **kwargs):
        return await func(*args, authorization, **kwargs)
    return wrapper
