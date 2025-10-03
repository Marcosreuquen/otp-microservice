from unittest.mock import MagicMock
from uuid import UUID

from app.controllers import userController, authController
from app.schemas.schemas import CreateUser


def test_get_user_not_found():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None

    res = userController.get_user("nosuch", mock_session)
    assert res is None


def test_user_exists_false():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None
    assert userController.user_exists("nosuch", mock_session) is False


def test_get_user_by_id_none():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None
    res = userController.get_user_by_id(UUID(int=1), mock_session)
    assert res is None


def test_create_auth_record_returns_true():
    # Mock a user-like object
    user = MagicMock()
    user.id = UUID(int=1)
    mock_session = MagicMock()

    # When session.commit/refresh are called, ensure auth record is present
    # Simulate that session.refresh sets a truthy auth record via return value
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    res = authController.create_auth_record(user, "hash", mock_session)
    assert res is True
