from pydantic import BaseModel, Field
from typing import Optional

class SendOtpRequest(BaseModel):
    phone: str = Field(..., description="Iranian phone number format")

class SendOtpResponse(BaseModel):
    message: str
    expires_in_seconds: int
    dev_code: Optional[str] = None

class VerifyOtpRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False

class AdminLoginRequest(BaseModel):
    username: str
    password: str
