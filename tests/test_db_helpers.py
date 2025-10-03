from unittest.mock import MagicMock
from uuid import UUID

from app.controllers import appController


def test_get_app_by_id_returns_record():
    mock_session = MagicMock()
    record = MagicMock()
    mock_session.exec.return_value.first.return_value = record

    res = appController.get_app_by_id(UUID(int=1), mock_session)
    assert res is record


def test_get_app_by_id_none():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None

    res = appController.get_app_by_id(UUID(int=1), mock_session)
    assert res is None
