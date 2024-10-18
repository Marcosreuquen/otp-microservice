from enum import Enum

class RecoveryMethod(Enum):
    EMAIL = 'EMAIL'
    SMS = 'SMS'

class OtpMethod(Enum):
    TOTP = 'TOTP'
    SMS = 'SMS'
    EMAIL = 'EMAIL'
    WHATSAPP = 'WHATSAPP'
