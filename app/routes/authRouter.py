from fastapi import APIRouter, status, Depends
from sqlmodel import Session

from app.controllers import authController, userController
from app.schemas import schemas
from app.models.db import get_session
from app.lib import jwt, oauth
from app.models.tables import User
from app.utils.exceptionHandler import ExceptionService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/", status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse
)
async def create_user(user: schemas.CreateUser, session: Session = Depends(get_session)):
     user_exist = userController.user_exists(user.username, session)
     ExceptionService.handle(not user_exist, 403, "User already exists")

     password_hash = jwt.hash(user.password)
     new_user: User = userController.create_user(user, session)
     ExceptionService.handle(new_user, 500, "Something went wrong")
     auth_record: bool = authController.create_auth_record(new_user, password_hash, session)
     ExceptionService.handle(auth_record, 500, "Something went wrong")
     return new_user


@router.post("/login", response_model=schemas.Token)
async def login(
    user_credentials: schemas.UserCredentials,
    db: Session = Depends(get_session),
):
    user = userController.get_user(user_credentials.username, db)
    ExceptionService.handle(user, 403)

    auth_record = authController.get_auth_record(user.id, db)
    verification = jwt.verify(user_credentials.password, auth_record.password_hash)
    ExceptionService.handle(verification, 403)

    access_token = oauth.create_access_token(data={"user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/recovery")
async def recovery_auth():
    return {}
