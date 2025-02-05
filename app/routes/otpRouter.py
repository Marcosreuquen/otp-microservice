from fastapi import APIRouter, Depends, Request, status
from sqlmodel import Session
from uuid import UUID

from app.models.db import get_session
from app.models.tables import AuthService
from app.utils.decorators import RequiresAuthentication
from app.controllers import authServiceController, userController, appController
from app.schemas import schemas
from app.lib.qr import generate_qr
from app.lib.otp import generate_uri, parse_uri
from fastapi.responses import StreamingResponse

from app.utils.exceptionHandler import ExceptionService

router = APIRouter(prefix="/otp", tags=["otp"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
@RequiresAuthentication
def create_user(body: schemas.OTPRegister, user_id: UUID, session: Session = Depends(get_session)):
    user = userController.get_user(body.username, session)
    ExceptionService.handle(user, 404, "User not found")
    body.user_id = user.id

    app = appController.get_app_by_id(body.app_id, session)
    ExceptionService.handle(app, 404, "App not found")
    service_record: AuthService = authServiceController.register_otp(body, session)
    ExceptionService.handle(service_record, 409, "User already registered")

    uri = generate_uri(service_record.otp_secret, app.name, user.username)
    qr = generate_qr(uri)
    return StreamingResponse(qr, media_type="image/png", status_code=status.HTTP_201_CREATED)

@router.put("/disable")
@RequiresAuthentication
async def disable_otp(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id
    ExceptionService.handle(user_id and app_id, 401)

    succeed = authServiceController.disable_otp(user_id, app_id, session)
    return {"success": succeed}

@router.put("/enable")
@RequiresAuthentication
async def enable_otp(body: schemas.BodyWithUri, request: Request, session: Session = Depends(get_session)):
    parsed_uri = parse_uri(body.uri)
    ExceptionService.handle(parsed_uri, 400, "Invalid URI")

    user = userController.get_user(parsed_uri.name, session)
    ExceptionService.handle(user and user.id == request.state.user_id, 404, "User not found")

    app = appController.get_app_by_name(parsed_uri.issuer, session)
    ExceptionService.handle(app, 404, "App not found")

    succeed = authServiceController.enable_otp(user.id, app.id, session)

    return { "success": succeed }

@router.get("/status")
@RequiresAuthentication
async def status_otp(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    ExceptionService.handle(app_id and user_id, 401)
    otp_enabled = authServiceController.status_otp(user_id, app_id, session)
    return {"enabled": otp_enabled}

@router.put("/recovery")
@RequiresAuthentication
async def recovery_otp(body: schemas.RecoveryOTPData, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    ExceptionService.handle(user_id and body.app_id, 401)
    succeed = authServiceController.recovery_otp(user_id, body, session)
    return {"success": succeed}