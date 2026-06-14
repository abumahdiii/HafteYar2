from fastapi import Depends, HTTPException, status
import os
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from src.infrastructure.database.session import get_db
from src.infrastructure.config.settings import settings

from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.otp_repository import OtpRepository
from src.infrastructure.gateways.sms.client import KavenegarSmsGateway

from src.infrastructure.database.repositories.team_repository import TeamRepository
from src.infrastructure.database.repositories.project_repository import ProjectRepository, ListRepository
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.infrastructure.database.repositories.subscription import (
    SQLAlchemySubscriptionRepository
)

from src.application.use_cases.auth import AuthUseCase
from src.application.use_cases.team_management import TeamManagementUseCase
from src.application.use_cases.task_management import TaskManagementUseCase
from src.application.use_cases.subscription import SubscriptionUseCase
from src.application.ai.middleware import AIMiddleware
from src.application.ai.executor import PlanExecutor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login/verify-otp")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id

def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    access_denied = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        if role != "admin":
            raise access_denied
    except JWTError:
        raise credentials_exception
    return user_id

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

def get_team_use_case(db: Session = Depends(get_db)) -> TeamManagementUseCase:
    return TeamManagementUseCase(
        team_repo=TeamRepository(db),
        project_repo=ProjectRepository(db),
        list_repo=ListRepository(db)
    )

def get_task_use_case(db: Session = Depends(get_db)) -> TaskManagementUseCase:
    return TaskManagementUseCase(
        task_repo=TaskRepository(db),
        project_repo=ProjectRepository(db),
        team_repo=TeamRepository(db)
    )

def get_subscription_use_case(db: Session = Depends(get_db)) -> SubscriptionUseCase:
    return SubscriptionUseCase(
        subscription_repo=SQLAlchemySubscriptionRepository(db)
    )

from src.application.ai.llm_provider import GeminiProvider

def get_ai_middleware(db: Session = Depends(get_db)) -> AIMiddleware:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    provider = GeminiProvider(api_key=api_key)
    return AIMiddleware(db_session=db, llm_provider=provider)

def get_plan_executor(db: Session = Depends(get_db)) -> PlanExecutor:
    return PlanExecutor(db_session=db)

from src.infrastructure.gateways.unified_input import UnifiedInputGateway

def get_unified_input_gateway(ai_middleware: AIMiddleware = Depends(get_ai_middleware)) -> UnifiedInputGateway:
    return UnifiedInputGateway(ai_middleware=ai_middleware)
