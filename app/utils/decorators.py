from fastapi import Request
from functools import wraps

from app.lib.oauth import get_token, verify_access_token
from app.utils.errors import require, Unauthorized


def RequiresAuthentication(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        auth_header = request.headers.get("Authorization")
        require(auth_header, Unauthorized("Authorization header missing"))
        token = get_token(auth_header)
        require(token, Unauthorized("Invalid or missing token"))
        data = verify_access_token(token)
        request.state.user_id = data.id
        return await func(*args, **kwargs)
    return wrapper
