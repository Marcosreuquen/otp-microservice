from fastapi import APIRouter
from app.utils.schemas import *
router = APIRouter(prefix="/mfa", tags=["mfa"])

@router.post("/register")
async def register_mfa():
    return {}

@router.post("/disable")
async def disable_mfa():
    return {}

@router.get("/status")
async def status_mfa():
    return {}

@router.post("/renew")
async def renew_mfa():
    return {}

@router.post("/revoke")
async def revoke_mfa():
    return {}