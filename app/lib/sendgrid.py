import sendgrid
import os

from pydantic import EmailStr
from sendgrid.helpers.mail import *
from config import settings

sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

def send_email(to: EmailStr, subject: str, body: str, mime_type: str = "text/plain"):
    from_email = Email(settings.EMAIL_ADDRES)
    to_email = To(to)
    subject = subject
    content = Content(mime_type, body)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)