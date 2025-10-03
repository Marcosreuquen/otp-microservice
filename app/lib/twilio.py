from twilio.rest import Client

from config import settings

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_phone_number = settings.TWILIO_PHONE_NUMBER
twilio_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
twilio_whatsapp_content_sid = settings.TWILIO_WHATSAPP_CONTENT_SID
client = Client(username=account_sid, password=auth_token)

def send_sms(to: str, body: str):
    try:
        message = client.messages.create(
            body=body,
            from_=twilio_phone_number,
            to=to
        )
        return message
    except Exception as e:
        # Log and return None so callers can translate to InternalError via require(...)
        from app.utils.logger import Logger
        Logger.error(f"Twilio send_sms failed: {e}")
        return None

def send_whatsapp(to: str, code: str):
    try:
        message = client.messages.create(
            content_variables='{"1": "'+code+'"}',
            content_sid=twilio_whatsapp_content_sid,
            from_="whatsapp:" + twilio_whatsapp_number,
            to="whatsapp:" + to,
        )
        return message
    except Exception as e:
        from app.utils.logger import Logger
        Logger.error(f"Twilio send_whatsapp failed: {e}")
        return None
