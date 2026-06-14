import logging
from fastapi import FastAPI
from src.infrastructure.config.settings import settings

from src.infrastructure.entrypoints.api.v1.auth import router as auth_router
from src.infrastructure.entrypoints.api.v1.teams import router as teams_router
from src.infrastructure.entrypoints.api.v1.tasks import router as tasks_router
from src.infrastructure.entrypoints.api.v1.subscriptions import router as subscriptions_router
from src.infrastructure.entrypoints.api.v1.ai import router as ai_router
from src.infrastructure.entrypoints.api.v1.bot_router import router as bot_router

from src.infrastructure.entrypoints.exception_handlers import (
    ResourceNotFoundError, resource_not_found_handler,
    AccessDeniedError, access_denied_handler,
    InvalidOperationError, invalid_operation_handler,
    RateLimitExceededError, rate_limit_exceeded_handler,
    DomainError, base_domain_error_handler
)

logging.basicConfig(level=logging.INFO)

from contextlib import asynccontextmanager
from src.infrastructure.database.session import engine, Base, SessionLocal
import src.infrastructure.database.models # Ensure all models are registered
from src.infrastructure.database.models.user import User
from src.domain.utils.security import get_password_hash

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database
    Base.metadata.create_all(bind=engine)
    
    # Seed Admin User
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            new_admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                is_admin=True,
                phone="00000000000" # Dummy phone to satisfy uniqueness if needed
            )
            db.add(new_admin)
            db.commit()
    finally:
        db.close()
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hafte-Yar API",
        version="1.0.0",
        description="REST API for Hafte-Yar Platform",
        lifespan=lifespan
    )

    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from src.infrastructure.entrypoints.api.v1.admin.users import router as admin_users_router
    from src.infrastructure.entrypoints.api.v1.admin.teams import router as admin_teams_router
    from src.infrastructure.entrypoints.api.v1.admin.settings import router as admin_settings_router
    from src.infrastructure.entrypoints.api.v1.admin.conversations import router as admin_conversations_router
    from src.infrastructure.entrypoints.api.v1.admin.tasks import router as admin_tasks_router
    from src.infrastructure.entrypoints.api.v1.admin.subscriptions import router as admin_subscriptions_router
    from src.infrastructure.entrypoints.api.v1.admin.ai_admin import router as ai_admin_router

    # Register Routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(teams_router, prefix="/api/v1")
    app.include_router(tasks_router, prefix="/api/v1")
    app.include_router(subscriptions_router, prefix="/api/v1")
    app.include_router(ai_router, prefix="/api/v1")
    app.include_router(bot_router, prefix="/api/v1")
    
    # Admin Routers
    app.include_router(admin_users_router, prefix="/api/v1/admin")
    app.include_router(admin_teams_router, prefix="/api/v1/admin")
    app.include_router(admin_settings_router, prefix="/api/v1/admin")
    app.include_router(admin_conversations_router, prefix="/api/v1/admin")
    app.include_router(admin_tasks_router, prefix="/api/v1/admin")
    app.include_router(admin_subscriptions_router, prefix="/api/v1/admin")
    app.include_router(ai_admin_router, prefix="/api/v1/admin")

    # Register Exception Handlers
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
    app.add_exception_handler(AccessDeniedError, access_denied_handler)
    app.add_exception_handler(InvalidOperationError, invalid_operation_handler)
    app.add_exception_handler(RateLimitExceededError, rate_limit_exceeded_handler)
    app.add_exception_handler(DomainError, base_domain_error_handler)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
