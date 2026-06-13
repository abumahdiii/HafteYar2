from sqlalchemy import Column, String, DateTime, Integer, Enum as SAEnum
from datetime import datetime
from src.infrastructure.database.session import Base
from src.domain.entities.enums import OtpPurpose

class OtpVerification(Base):
    __tablename__ = "otp_verifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(11), nullable=False, index=True)
    code_hash = Column(String, nullable=False)
    purpose = Column(SAEnum(OtpPurpose), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    attempts = Column(Integer, nullable=False, default=0)
