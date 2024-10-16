from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.models.db import get_session
from app.utils.decorators import RequiresAuthentication
from app.controllers import authServiceController, userController, appController
from app.schemas import schemas
from app.lib.qr import generate_qr
from app.lib.otp import generate_uri, parse_uri
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/mfa", tags=["mfa"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
@RequiresAuthentication
def create_user(body: schemas.MFARegister, user_id: UUID, request: Request, session: Session = Depends(get_session)):
    owner_id = request.state.user_id
    if not user_id or not owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if not body:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Missing body")

    user = userController.get_user_by_id(user_id, session)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    app = appController.get_app_by_id(body.app_id, session)

    if not app:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not found")


    serviceRecord = authServiceController.register_mfa(body, session)

    if not serviceRecord:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="User already registered")

    uri = generate_uri(serviceRecord.otp_secret, app.name, user.username)

    qr = generate_qr(uri)

    return StreamingResponse(qr, media_type="image/png", status_code=status.HTTP_201_CREATED)

@router.put("/disable")
@RequiresAuthentication
async def disable_mfa(body: schemas.BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    succeed = authServiceController.disable_mfa(user_id, app_id, session)
    return {"success": succeed}

@router.put("/enable")
@RequiresAuthentication
async def enable_mfa(body: schemas.BodyWithUri, request: Request, session: Session = Depends(get_session)):
    parsed_uri = parse_uri(body.uri)

    if not parsed_uri:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid URI")

    user = userController.get_user(parsed_uri.name, session)

    if not user or user.id != request.state.user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    app = appController.get_app_by_name(parsed_uri.issuer, session)

    if not app:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not found")

    succeed = authServiceController.enable_mfa(user.id, app.id, session)
    
    return { "success": succeed }

@router.get("/status")
@RequiresAuthentication
async def status_mfa(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    mfa_enabled = authServiceController.status_mfa(user_id, app_id, session)
    return {"enabled": mfa_enabled}

@router.put("/recovery")
@RequiresAuthentication
async def recovery_mfa(body: schemas.RecoveryMFAData, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    succeed = authServiceController.recovery_mfa(user_id, body, session)
    return {"success": succeed}