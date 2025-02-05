import resend

from pydantic import EmailStr
from config import settings

resend.api_key = settings.RESEND_API_KEY


def send_email(
    to: EmailStr,
    subject: str,
    body: str,):
    
    params: resend.Emails.SendParams = {
        "from": settings.EMAIL_ADDRESS,
        "to": [to],
        "subject": subject,
        "text": body
    }
    
    email = resend.Emails.send(params)
    return  email

def get_template(app_name: str, code: str) -> str:
    html_template = """\
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding: 20px;
            }}
            .container {{
                background-color: #ffffff;
                max-width: 400px;
                margin: auto;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .code {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: #f8f8f8;
                display: inline-block;
                border-radius: 5px;
                margin: 10px 0;
            }}
            .footer {{
                font-size: 12px;
                color: #888;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Your verification code for <strong>{app_name}</strong></h2>
            <p>Use the following code to sign in to <strong>{app_name}</strong></p>
            <div class="code">{code}</div>
            <p>This code is valid for a limited time.</p>
            <p class="footer">If you did not request this code, please ignore this message.</p>
        </div>
    </body>
    </html>
    """
    return html_template.format(app_name=app_name, code=code)