# Integration-style test using SQLModel with in-memory SQLite to exercise create_user and create_auth_record
import os
import tempfile
from sqlmodel import SQLModel, Session, create_engine
from app.models.tables import User, Auth
from app.controllers import userController, authController
from app.schemas.schemas import CreateUser


def test_create_user_and_auth_integration():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Create a user
        user_in = CreateUser(email="test@example.com", password="pw", username="tester")
        user = userController.create_user(user_in, session)
        assert user.username == "tester"

        # Create auth record for that user
        result = authController.create_auth_record(user, "hash123", session)
        assert result is True
