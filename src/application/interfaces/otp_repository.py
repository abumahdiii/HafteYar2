from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.enums import OtpPurpose

class IOtpRepository(ABC):
    @abstractmethod
    def save_otp(self, phone: str, code_hash: str, purpose: OtpPurpose, expires_in_minutes: int) -> int:
        pass

    @abstractmethod
    def get_active_otp(self, phone: str, purpose: OtpPurpose) -> Optional[dict]:
        """Returns OTP details if valid and unexpired."""
        pass

    @abstractmethod
    def increment_attempts(self, otp_id: int) -> None:
        pass

    @abstractmethod
    def delete_otp(self, otp_id: int) -> None:
        pass
