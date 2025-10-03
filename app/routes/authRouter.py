from fastapi import APIRouter, status, Depends
from sqlmodel import Session

from app.controllers import authController, userController
from app.schemas import schemas
from app.models.db import get_session
from app.lib import jwt, oauth
from app.models.tables import User
from app.utils.errors import require, NotFound, Conflict, InternalError, Unauthorized

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/", status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse
)
async def create_user(user: schemas.CreateUser, session: Session = Depends(get_session)):
    user_exist = userController.user_exists(user.username, session)
    require(not user_exist, Conflict("User already exists"))

    password_hash = jwt.hash(user.password)
    new_user: User = userController.create_user(user, session)
    require(new_user, InternalError("Failed to create user"))
    auth_record: bool = authController.create_auth_record(new_user, password_hash, session)
    require(auth_record, InternalError("Failed to create auth record"))
    return new_user


@router.post("/login", response_model=schemas.Token)
async def login(
    user_credentials: schemas.UserCredentials,
    db: Session = Depends(get_session),
):
    user = userController.get_user(user_credentials.username, db)
    require(user, NotFound("User not found"))

    auth_record = authController.get_auth_record(user.id, db)
    verification = jwt.verify(user_credentials.password, auth_record.password_hash)
    require(verification, Unauthorized("Invalid credentials"))

    access_token = oauth.create_access_token(data={"user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/recovery")
async def recovery_auth():
    return {}
