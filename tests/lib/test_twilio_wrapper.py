from unittest.mock import patch
from app.lib.twilio import send_sms, send_whatsapp


def test_send_sms_handles_exceptions(monkeypatch):
    class FakeException(Exception):
        pass

    def fake_create(*args, **kwargs):
        raise FakeException("boom")

    with patch("app.lib.twilio.client.messages.create", side_effect=fake_create):
        res = send_sms("+123", "hi")
        assert res is None


def test_send_whatsapp_handles_exceptions(monkeypatch):
    class FakeException(Exception):
        pass

    def fake_create(*args, **kwargs):
        raise FakeException("boom")

    with patch("app.lib.twilio.client.messages.create", side_effect=fake_create):
        res = send_whatsapp("+123", "0000")
        assert res is None
