from unittest.mock import patch
from app.lib.resend import send_email


def test_send_email_handles_exceptions():
    class FakeException(Exception):
        pass

    def fake_send(params):
        raise FakeException("boom")

    with patch("app.lib.resend.resend.Emails.send", side_effect=fake_send):
        res = send_email("test@example.com", "subj", "body")
        assert res is None
