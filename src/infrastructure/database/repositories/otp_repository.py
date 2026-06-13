from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from src.application.interfaces.otp_repository import IOtpRepository
from src.domain.entities.enums import OtpPurpose
from src.infrastructure.database.models.otp import OtpVerification

class OtpRepository(IOtpRepository):
    def __init__(self, db: Session):
        self.db = db

    def save_otp(self, phone: str, code_hash: str, purpose: OtpPurpose, expires_in_minutes: int) -> int:
        # Delete existing active OTP for this purpose
        self.db.query(OtpVerification).filter(
            OtpVerification.phone == phone,
            OtpVerification.purpose == purpose
        ).delete()
        
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        otp = OtpVerification(
            phone=phone,
            code_hash=code_hash,
            purpose=purpose,
            expires_at=expires_at
        )
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        return otp.id

    def get_active_otp(self, phone: str, purpose: OtpPurpose) -> Optional[dict]:
        otp = self.db.query(OtpVerification).filter(
            OtpVerification.phone == phone,
            OtpVerification.purpose == purpose,
            OtpVerification.expires_at > datetime.utcnow()
        ).first()
        
        if otp:
            return {
                "id": otp.id,
                "code_hash": otp.code_hash,
                "attempts": otp.attempts,
                "expires_at": otp.expires_at
            }
        return None

    def increment_attempts(self, otp_id: int) -> None:
        otp = self.db.query(OtpVerification).filter(OtpVerification.id == otp_id).first()
        if otp:
            otp.attempts += 1
            self.db.commit()

    def delete_otp(self, otp_id: int) -> None:
        self.db.query(OtpVerification).filter(OtpVerification.id == otp_id).delete()
        self.db.commit()
