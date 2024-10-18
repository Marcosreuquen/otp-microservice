from twilio.rest import Client

from config import settings

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_phone_number = settings.TWILIO_PHONE_NUMBER
twilio_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
twilio_whatsapp_content_sid = settings.TWILIO_WHATSAPP_CONTENT_SID
client = Client(username=account_sid, password=auth_token)

def send_sms(to: str, body: str):
    message = client.messages.create(
        body=body,
        from_=twilio_phone_number,
        to=to
    )
    return message

def send_whatsapp(to: str, code: str):
    message =client.messages.create(
        content_variables='{"1": "'+code+'"}',
        content_sid=twilio_whatsapp_content_sid,
        from_="whatsapp:" + twilio_whatsapp_number,
        to="whatsapp:" + to,
    )
    return message

