from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RESEND_API_KEY: str
    EMAIL_ADDRESS: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    TWILIO_WHATSAPP_NUMBER: str
    TWILIO_WHATSAPP_CONTENT_SID: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    REDIS_URL: str
    # Optional explicit fallback redis URL (e.g. redis://127.0.0.1:6379)
    REDIS_FALLBACK: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
