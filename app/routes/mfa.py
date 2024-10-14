from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlmodel import Session

from app.models.db import get_session
from app.decorators import RequiresAuthentication
import app.controllers.service as authServiceController
from app.utils.schemas import *



router = APIRouter(prefix="/mfa", tags=["mfa"])

@router.post("/register")
@RequiresAuthentication
async def register_mfa(data : MFARegister, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    record = authServiceController.register_mfa(user_id, data, session)
    return record

@router.put("/disable")
@RequiresAuthentication
async def disable_mfa(body: BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    succeed = authServiceController.disable_mfa(user_id, app_id, session)
    return {"success": succeed}

@router.put("/enable")
@RequiresAuthentication
async def enable_mfa(body: BodyWithAppId, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id
    app_id = body.app_id

    if not user_id or not app_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    succeed = authServiceController.enable_mfa(user_id, app_id, session)
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
async def recovery_mfa(body:RecoveryMFAData, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    succeed = authServiceController.recovery_mfa(user_id, body, session)
    return {"success": succeed}

@router.post("/renew")
@RequiresAuthentication
async def renew_mfa(request: Request, session: Session = Depends(get_session)):
    return {}

@router.post("/revoke")
@RequiresAuthentication
async def revoke_mfa(request: Request, session: Session = Depends(get_session)):
    return {}