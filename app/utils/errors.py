from typing import Optional
from app.utils.exceptionHandler import ApiException


class BadRequest(ApiException):
    def __init__(self, detail: str = "Bad Request", extra: Optional[dict] = None):
        super().__init__(status_code=400, detail=detail, extra=extra)


class Unauthorized(ApiException):
    def __init__(self, detail: str = "Unauthorized", extra: Optional[dict] = None):
        super().__init__(status_code=401, detail=detail, extra=extra)


class Forbidden(ApiException):
    def __init__(self, detail: str = "Forbidden", extra: Optional[dict] = None):
        super().__init__(status_code=403, detail=detail, extra=extra)


class NotFound(ApiException):
    def __init__(self, detail: str = "Not Found", extra: Optional[dict] = None):
        super().__init__(status_code=404, detail=detail, extra=extra)


class Conflict(ApiException):
    def __init__(self, detail: str = "Conflict", extra: Optional[dict] = None):
        super().__init__(status_code=409, detail=detail, extra=extra)


class InternalError(ApiException):
    def __init__(self, detail: str = "Internal Server Error", extra: Optional[dict] = None):
        super().__init__(status_code=500, detail=detail, extra=extra)


def require(condition: bool, exc: Exception):
    """Helper: raise given exception if condition is False.

    Usage: require(user, NotFound("User not found"))
    """
    if not condition:
        raise exc
