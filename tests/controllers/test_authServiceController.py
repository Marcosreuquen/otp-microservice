from unittest.mock import MagicMock
from uuid import UUID

from app.controllers import authServiceController
from app.utils.errors import NotFound


def test_get_service_with_user_and_app_not_found():
    session = MagicMock()
    # Setup session.exec(...).first() to return None
    session.exec.return_value.first.return_value = None
    res = authServiceController.get_service_with_user_and_app("user-1", UUID(int=1), session)
    assert res is None


def test_get_secret_returns_value():
    session = MagicMock()
    # Mock a record object with otp_secret
    record = MagicMock()
    record.otp_secret = "SECRET"
    session.exec.return_value.first.return_value = record

    secret = authServiceController.get_secret("user-1", UUID(int=1), session)
    assert secret == "SECRET"
