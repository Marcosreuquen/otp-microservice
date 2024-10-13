from pyotp import TOTP, random_base32


def generate_secret():
    return random_base32()

def generate_otp(secret):
    return TOTP(secret).provisioning_uri("test", issuer_name="test")

def verify_otp(secret, otp):
    return TOTP(secret).verify(otp)