from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import traceback

from app.utils.logger import Logger


class ApiException(HTTPException):
    def __init__(self, status_code: int = 500, detail: str = "Internal Server Error", extra: dict | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.extra = extra or {}


# The ExceptionService check/handle helpers were removed in favor of explicit
# domain exceptions (see `app/utils/errors.py`) and the `require(...)` helper.
# Keep ApiException and the FastAPI handler below.


def fastapi_exception_handler(request: Request, exc: Exception):
    """Generic exception handler that returns structured JSON and logs details."""
    # ApiException (our wrapper) or HTTPException
    if isinstance(exc, ApiException):
        payload = {"error": True, "message": exc.detail}
        if getattr(exc, "extra", None):
            payload.update(exc.extra)
        Logger.warning(f"Handled ApiException: {exc.status_code} - {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content=payload)

    if isinstance(exc, HTTPException):
        Logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"error": True, "message": exc.detail})

    # Unhandled exception
    tb = traceback.format_exc()
    Logger.error(f"Unhandled exception: {str(exc)}")
    Logger.debug(tb)
    return JSONResponse(status_code=500, content={"error": True, "message": "Internal Server Error"})