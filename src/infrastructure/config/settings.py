from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DEV_MODE: bool = Field(default=True, env="DEV_MODE")
    ENV: str = "dev"
    DATABASE_URL: str = Field(default="sqlite:///./haftyar.db", env="DATABASE_URL")
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ALGORITHM: str = "HS256"
    
    SMS_PROVIDER: str = "console"
    SMS_API_KEY: str = ""
    SMS_TEMPLATE: str = "hafteyar-otp"
    
    OTP_EXPIRE_MINUTES: int = 5
    OTP_RESEND_SECONDS: int = 60
    OTP_MAX_ATTEMPTS: int = 5
    
    TELEGRAM_BOT_TOKEN: str = ""
    BALE_BOT_TOKEN: str = ""
    
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
