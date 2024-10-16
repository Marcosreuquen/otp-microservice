# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

from config import settings

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

def send_sms(to: str, body: str):
    client.messages.create(
        messaging_service_sid="MG9752274e9e519418a7406176694466fa",
        to=to,
        body=body
    )

def send_whatsapp(to: str, body: str):
    client.messages.create(
        body=body,
        from_="whatsapp:" + settings.TWILIO_WHATSAPP_NUMBER,
        to="whatsapp:" + to,
    )

