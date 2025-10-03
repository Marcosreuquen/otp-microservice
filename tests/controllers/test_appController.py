from unittest.mock import MagicMock, patch
from uuid import UUID

from app.controllers import appController
from app.utils.errors import NotFound


def test_reset_api_key_secret_requires_record():
    mock_session = MagicMock()
    # session.exec(...).first() returns None
    mock_session.exec.return_value.first.return_value = None

    try:
        appController.reset_api_key_secret(UUID(int=1), UUID(int=2), mock_session)
        raised = False
    except NotFound:
        raised = True

    assert raised is True


def test_reset_api_key_secret_updates_secret():
    # Mock a record object with name and owner_id
    record = MagicMock()
    record.name = "record1"
    record.owner_id = UUID(int=2)

    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = record

    # Patch the generate_secret to return a deterministic value
    with patch("app.controllers.appController.generate_secret", return_value="secret"):
        res = appController.reset_api_key_secret(UUID(int=1), UUID(int=2), mock_session)

    assert hasattr(res, "api_key_secret")
    assert res.api_key_secret.endswith("secret")
