from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.config.settings import settings
from src.infrastructure.entrypoints.api.v1.auth import router as auth_router
from src.infrastructure.entrypoints.webhooks.router import router as webhook_router
from src.domain.exceptions import (
    DomainError, ResourceNotFoundError, AccessDeniedError,
    InvalidOperationError, RateLimitExceededError
)
from src.infrastructure.entrypoints.exception_handlers import (
    base_domain_error_handler, resource_not_found_handler,
    access_denied_handler, invalid_operation_handler,
    rate_limit_exceeded_handler
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hafte-Yar API",
        version="0.4.0",
        description="Clean Architecture Refactor of Hafte-Yar"
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
    app.add_exception_handler(AccessDeniedError, access_denied_handler)
    app.add_exception_handler(InvalidOperationError, invalid_operation_handler)
    app.add_exception_handler(RateLimitExceededError, rate_limit_exceeded_handler)
    app.add_exception_handler(DomainError, base_domain_error_handler)

    # Routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(webhook_router, prefix="/api/v1")

    return app

app = create_app()
