from fastapi import HTTPException, status

from app.utils.logger import Logger

class ExceptionService:
    status_mapping = {
        400: status.HTTP_400_BAD_REQUEST,
        401: status.HTTP_401_UNAUTHORIZED,
        402: status.HTTP_402_PAYMENT_REQUIRED,
        403: status.HTTP_403_FORBIDDEN,
        404: status.HTTP_404_NOT_FOUND,
        405: status.HTTP_405_METHOD_NOT_ALLOWED,
        406: status.HTTP_406_NOT_ACCEPTABLE,
        407: status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED,
        408: status.HTTP_408_REQUEST_TIMEOUT,
        409: status.HTTP_409_CONFLICT,
        429: status.HTTP_429_TOO_MANY_REQUESTS,
        451: status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
        500: status.HTTP_500_INTERNAL_SERVER_ERROR,
        502: status.HTTP_502_BAD_GATEWAY,
        503: status.HTTP_503_SERVICE_UNAVAILABLE
    }

    detail_mapping = {
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        429: "Too Many Requests",
        451: "Unavailable For Legal Reasons",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable"
    }

    @staticmethod
    def handle(condition , code = 500, detail=""):
        if not detail:
            detail = ExceptionService.detail_mapping[code]

        if not condition:
            Logger.error(f"Error: {code} - {detail}")
            raise HTTPException(
                status_code=ExceptionService.status_mapping[code],
                detail=detail)