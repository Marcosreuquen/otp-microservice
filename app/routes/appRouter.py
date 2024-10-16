from fastapi import APIRouter, status, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from uuid import UUID

from app.lib.otp import generate_uri
from app.models.db import get_session
from app.utils.decorators import RequiresAuthentication
import app.schemas.schemas as schemas
from app.controllers import appController, authServiceController
from app.lib.qr import generate_qr

router = APIRouter(prefix="/app", tags=["app"])

@router.post("/", status_code=status.HTTP_201_CREATED)
@RequiresAuthentication
def create_app(body: schemas.CreateApp, request: Request, session: Session = Depends(get_session)):
    if not request.state.user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = request.state.user_id

    new_app = appController.create_app(user_id, body.name, session)
    return new_app

@router.get("/{app_id}", status_code=status.HTTP_200_OK)
@RequiresAuthentication
def get_app(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    app = appController.get_app_by_id(app_id, session)
    return app

@router.put("/{app_id}", status_code=status.HTTP_200_OK)
@RequiresAuthentication
def update_app(app_id: UUID, body: schemas.UpdateApp, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not app_id or not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    app = appController.update_app_name(app_id, user_id, body.name, session)
    return app

@router.delete("/{app_id}", status_code=status.HTTP_200_OK)
@RequiresAuthentication
def delete_app(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not app_id or not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    app = appController.delete_app(user_id, app_id, session)
    return app

@router.put("/{app_id}/api-key", status_code=status.HTTP_201_CREATED)
@RequiresAuthentication
def create_api_key(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not app_id or not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    app = appController.reset_api_key_secret(app_id, user_id, session)
    return app

@router.get("/{app_id}/api-key", status_code=status.HTTP_200_OK)
@RequiresAuthentication
def get_api_key(app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not app_id or not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    app = appController.get_api_key_secret(app_id, user_id, session)
    return app

@router.get("/{app_id}/users", status_code=status.HTTP_200_OK)
@RequiresAuthentication
def get_users( app_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_id = request.state.user_id

    if not app_id or not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    app = appController.get_user_apps(user_id, app_id, session)
    return app

