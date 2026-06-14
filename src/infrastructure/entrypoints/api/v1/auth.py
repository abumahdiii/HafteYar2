from fastapi import APIRouter, Depends, status
from src.infrastructure.entrypoints.schemas.auth_schemas import (
    SendOtpRequest, SendOtpResponse, VerifyOtpRequest, TokenResponse, AdminLoginRequest
)
from src.application.use_cases.auth import AuthUseCase
from src.infrastructure.entrypoints.dependencies import get_auth_use_case
from src.domain.entities.enums import OtpPurpose

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/send-otp", response_model=SendOtpResponse)
def register_send_otp(
    request: SendOtpRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case)
):
    expires_in, dev_code = use_case.request_otp(request.phone, OtpPurpose.REGISTER)
    return SendOtpResponse(
        message="Verification code sent.",
        expires_in_seconds=expires_in,
        dev_code=dev_code
    )

@router.post("/register/verify-otp", response_model=TokenResponse)
def register_verify_otp(
    request: VerifyOtpRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case)
):
    token, is_new = use_case.verify_otp(request.phone, request.code, OtpPurpose.REGISTER)
    return TokenResponse(access_token=token, is_new_user=is_new)

@router.post("/login/send-otp", response_model=SendOtpResponse)
def login_send_otp(
    request: SendOtpRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case)
):
    expires_in, dev_code = use_case.request_otp(request.phone, OtpPurpose.LOGIN)
    return SendOtpResponse(
        message="Verification code sent.",
        expires_in_seconds=expires_in,
        dev_code=dev_code
    )

@router.post("/login/verify-otp", response_model=TokenResponse)
def login_verify_otp(
    request: VerifyOtpRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case)
):
    token, is_new = use_case.verify_otp(request.phone, request.code, OtpPurpose.LOGIN)
    return TokenResponse(access_token=token, is_new_user=is_new)

@router.post("/admin/login", response_model=TokenResponse)
def admin_login(
    request: AdminLoginRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case)
):
    token = use_case.admin_login(request.username, request.password)
    return TokenResponse(access_token=token, is_new_user=False)
