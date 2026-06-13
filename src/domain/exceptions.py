class DomainError(Exception):
    """Base class for domain exceptions"""
    pass

class ResourceNotFoundError(DomainError):
    pass

class AccessDeniedError(DomainError):
    pass

class InvalidOperationError(DomainError):
    pass

class TeamSubscriptionExpiredError(InvalidOperationError):
    pass

class RateLimitExceededError(DomainError):
    pass
