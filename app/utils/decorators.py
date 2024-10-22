from fastapi import Request
from functools import wraps

from app.lib.oauth import get_token, verify_access_token
from app.utils.exceptionHandler import ExceptionService


def RequiresAuthentication(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        auth_header = request.headers.get("Authorization")

        ExceptionService.handle(auth_header, 401)
        token = get_token(auth_header)
        ExceptionService.handle(token, 401)
        try:
            data = verify_access_token(token)
            request.state.user_id = data.id
        finally:
            pass
        return await func(*args, **kwargs)
    return wrapper

