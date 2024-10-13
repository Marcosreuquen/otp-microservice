from fastapi import APIRouter


router = APIRouter(prefix="/code", tags=["code"])

@router.get("/generate")
async def generate_mfa():
    return {}

@router.get("/sms")
async def send_sms_mfa():
    return {}

@router.get("/email")
async def send_email_mfa():
    return {}

@router.post("/verify")
async def verify_mfa():
    return {}