import unittest
from app.lib.resend import get_template
from unittest.mock import patch, MagicMock
from app.lib.resend import send_email

class TestGetTemplate(unittest.TestCase):

    def test_get_template(self):
        app_name = "TestApp"
        code = "123456"
        expected_html =  """<html> <head> <style> body { font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center; padding: 20px; } .container { background-color: #ffffff; max-width: 400px; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); } .code { font-size: 24px; font-weight: bold; color: #333; padding: 10px; background-color: #f8f8f8; display: inline-block; border-radius: 5px; margin: 10px 0; } .footer { font-size: 12px; color: #888; margin-top: 20px; } </style> </head> <body> <div class="container"> <h2>Your verification code for <strong>TestApp</strong></h2> <p>Use the following code to sign in to <strong>TestApp</strong></p> <div class="code">123456</div> <p>This code is valid for a limited time.</p> <p class="footer">If you did not request this code, please ignore this message.</p> </div> </body> </html>"""
        result = get_template(app_name, code)
        self.assertEqual(result, expected_html)

class TestSendEmail(unittest.TestCase):

    @patch('app.lib.resend.resend.Emails.send')
    @patch('app.lib.resend.settings')
    def test_send_email(self, mock_settings, mock_send):
        mock_settings.RESEND_API_KEY = "fake_api_key"
        mock_settings.EMAIL_ADDRESS = "test@example.com"
        
        to = "recipient@example.com"
        subject = "Test Subject"
        body = "Test Body"
        
        mock_send.return_value = MagicMock(status_code=200)
        
        response = send_email(to, subject, body)
        
        mock_send.assert_called_once_with({
            "from": "test@example.com",
            "to": [to],
            "subject": subject,
            "text": body
        })
        
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()