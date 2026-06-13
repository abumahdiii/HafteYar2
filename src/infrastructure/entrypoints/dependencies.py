from fastapi import Depends
from sqlalchemy.orm import Session
from src.infrastructure.database.session import get_db
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.otp_repository import OtpRepository
from src.infrastructure.gateways.sms.client import KavenegarSmsGateway
from src.application.use_cases.auth import AuthUseCase

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_otp_repository(db: Session = Depends(get_db)) -> OtpRepository:
    return OtpRepository(db)

def get_sms_gateway() -> KavenegarSmsGateway:
    return KavenegarSmsGateway()

def get_auth_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    otp_repo: OtpRepository = Depends(get_otp_repository),
    sms_gateway: KavenegarSmsGateway = Depends(get_sms_gateway)
) -> AuthUseCase:
    return AuthUseCase(user_repo=user_repo, otp_repo=otp_repo, sms_gateway=sms_gateway)
