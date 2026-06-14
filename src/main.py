import logging
from fastapi import FastAPI
from src.infrastructure.config.settings import settings

from src.infrastructure.entrypoints.api.v1.auth import router as auth_router
from src.infrastructure.entrypoints.api.v1.teams import router as teams_router
from src.infrastructure.entrypoints.api.v1.tasks import router as tasks_router
from src.infrastructure.entrypoints.api.v1.subscriptions import router as subscriptions_router
from src.infrastructure.entrypoints.api.v1.ai import router as ai_router

from src.infrastructure.entrypoints.exception_handlers import (
    ResourceNotFoundError, resource_not_found_handler,
    AccessDeniedError, access_denied_handler,
    InvalidOperationError, invalid_operation_handler,
    RateLimitExceededError, rate_limit_exceeded_handler,
    DomainError, base_domain_error_handler
)

logging.basicConfig(level=logging.INFO)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hafte-Yar API",
        version="1.0.0",
        description="REST API for Hafte-Yar Platform"
    )

    # Register Routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(teams_router, prefix="/api/v1")
    app.include_router(tasks_router, prefix="/api/v1")
    app.include_router(subscriptions_router, prefix="/api/v1")
    app.include_router(ai_router, prefix="/api/v1")

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
