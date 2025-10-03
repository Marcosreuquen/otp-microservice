from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.utils.errors import NotFound, InternalError

client = TestClient(app)


def fake_get_secret(user_id, app_id, session):
    return "SECRET123"


@patch("app.routes.codeRouter.get_service_with_user_and_app")
@patch("app.routes.codeRouter.authServiceController.get_secret", side_effect=fake_get_secret)
@patch("app.routes.codeRouter.send_sms", return_value=MagicMock())
@patch("app.routes.codeRouter.send_whatsapp", return_value=MagicMock())
@patch("app.routes.codeRouter.send_email", return_value=MagicMock())
@patch("app.routes.codeRouter.generate_otp_code", return_value="123456")
def test_generate_and_send_routes(mock_generate_otp, mock_send_email, mock_send_whatsapp, mock_send_sms, mock_get_secret, mock_service):
    # Prepare headers with a valid token for decorator (we bypass token validation by monkeypatching oauth)
    with patch("app.utils.decorators.verify_access_token", return_value=MagicMock(id="user-1")):
        headers = {"Authorization": "Bearer dummy"}

        # Generate code (redis is optional and may fail silently in route) - just ensure endpoint runs
        r = client.get("/api/code/generate/00000000-0000-0000-0000-000000000000", headers=headers)
        assert r.status_code == 200
        assert "code" in r.json()

        # send sms route
        body = {"app_id": "00000000-0000-0000-0000-000000000000"}
        r2 = client.post("/api/code/sms", json=body, headers=headers)
        assert r2.status_code == 200

        # send whatsapp
        r3 = client.post("/api/code/whatsapp", json=body, headers=headers)
        assert r3.status_code == 200

        # send email (now POST)
        r4 = client.post("/api/code/email", json=body, headers=headers)
        assert r4.status_code == 200


@patch("app.routes.codeRouter.authServiceController.get_secret", side_effect=lambda *a, **k: None)
def test_generate_requires_secret(mock_get_secret):
    with patch("app.utils.decorators.verify_access_token", return_value=MagicMock(id="user-1")):
        headers = {"Authorization": "Bearer dummy"}
        r = client.get("/api/code/generate/00000000-0000-0000-0000-000000000000", headers=headers)
    assert r.status_code == 404