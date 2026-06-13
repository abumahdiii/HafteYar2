from fastapi import Request
from fastapi.responses import JSONResponse
from src.domain.exceptions import (
    DomainError, ResourceNotFoundError, AccessDeniedError,
    InvalidOperationError, RateLimitExceededError
)

def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

def access_denied_handler(request: Request, exc: AccessDeniedError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

def invalid_operation_handler(request: Request, exc: InvalidOperationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceededError):
    return JSONResponse(status_code=429, content={"detail": str(exc)})

def base_domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=500, content={"detail": "An internal domain error occurred."})
