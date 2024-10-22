from pyotp import TOTP, random_base32, parse_uri as parse


def generate_secret():
    return random_base32()

def generate_otp(secret):
    return TOTP(secret).now()

def verify_otp(secret, otp):
    return TOTP(secret).verify(otp)

def generate_uri(secret, issuer_name, username):
    return TOTP(secret).provisioning_uri(username, issuer_name=issuer_name)

def parse_uri(uri):
    return parse(uri)