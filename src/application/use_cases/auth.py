import secrets
from typing import Tuple, Optional
from src.application.interfaces.repositories import IUserRepository
from src.application.interfaces.otp_repository import IOtpRepository
from src.application.interfaces.sms_gateway import ISmsGateway
from src.domain.entities.enums import OtpPurpose
from src.domain.entities.user import UserEntity, UserAccountEntity
from src.domain.utils.phone import normalize_phone
from src.domain.utils.security import get_password_hash, verify_password, create_access_token
from src.domain.exceptions import InvalidOperationError, ResourceNotFoundError, RateLimitExceededError
from src.infrastructure.config.settings import settings
from src.domain.utils.ids import new_account_id

class AuthUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        otp_repo: IOtpRepository,
        sms_gateway: ISmsGateway
    ):
        self.user_repo = user_repo
        self.otp_repo = otp_repo
        self.sms_gateway = sms_gateway

    def request_otp(self, phone: str, purpose: OtpPurpose) -> Tuple[int, Optional[str]]:
        """
        Initiates OTP process. Returns (expires_in_seconds, dev_code).
        dev_code is returned only if SMS provider is 'console'.
        """
        normalized_phone = normalize_phone(phone)
        user = self.user_repo.get_by_phone(normalized_phone)

        if purpose == OtpPurpose.REGISTER and user:
            raise InvalidOperationError("User with this phone number already exists.")
        if purpose == OtpPurpose.LOGIN and not user:
            raise ResourceNotFoundError("No user found with this phone number.")

        # Generate 6 digit code
        code = str(secrets.randbelow(1_000_000)).zfill(6)
        code_hash = get_password_hash(code)

        # Save to DB
        self.otp_repo.save_otp(
            phone=normalized_phone,
            code_hash=code_hash,
            purpose=purpose,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES
        )

        # Send SMS
        self.sms_gateway.send_otp(normalized_phone, code)

        dev_code = code if settings.SMS_PROVIDER == "console" else None
        return settings.OTP_EXPIRE_MINUTES * 60, dev_code

    def verify_otp(self, phone: str, code: str, purpose: OtpPurpose) -> Tuple[str, bool]:
        """
        Verifies OTP and returns (access_token, is_new_user).
        """
        normalized_phone = normalize_phone(phone)
        active_otp = self.otp_repo.get_active_otp(normalized_phone, purpose)

        if not active_otp:
            raise InvalidOperationError("No active verification code found or it has expired.")

        if active_otp["attempts"] >= settings.OTP_MAX_ATTEMPTS:
            self.otp_repo.delete_otp(active_otp["id"])
            raise RateLimitExceededError("Maximum verification attempts exceeded. Please request a new code.")

        if not verify_password(code, active_otp["code_hash"]):
            self.otp_repo.increment_attempts(active_otp["id"])
            raise InvalidOperationError("Invalid verification code.")

        # Success - remove OTP
        self.otp_repo.delete_otp(active_otp["id"])

        is_new_user = False
        user = self.user_repo.get_by_phone(normalized_phone)

        if purpose == OtpPurpose.REGISTER:
            if user:
                raise InvalidOperationError("User already exists.")
            
            # Create user
            new_user = UserEntity(phone=normalized_phone)
            # Create phone account
            account = UserAccountEntity(
                id=new_account_id(),
                user_id="", # Assigned by repo or later
                provider="phone",
                provider_id=normalized_phone
            )
            new_user.accounts.append(account)
            user = self.user_repo.create(new_user)
            is_new_user = True

        elif purpose == OtpPurpose.LOGIN and not user:
            raise ResourceNotFoundError("User not found.")

        access_token = create_access_token(data={"sub": user.id})
        return access_token, is_new_user
