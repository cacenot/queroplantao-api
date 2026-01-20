"""Custom application exceptions."""

from src.app.exceptions.base import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from src.app.exceptions.auth_exceptions import (
    AuthException,
    CacheError,
    ExpiredTokenError,
    FirebaseAuthError,
    FirebaseInitError,
    InvalidTokenError,
    MissingTokenError,
    RevokedTokenError,
    UserInactiveError,
    UserNotFoundError,
)

__all__ = [
    # Base exceptions
    "AppException",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "NotFoundError",
    "ValidationError",
    # Auth exceptions
    "AuthException",
    "CacheError",
    "ExpiredTokenError",
    "FirebaseAuthError",
    "FirebaseInitError",
    "InvalidTokenError",
    "MissingTokenError",
    "RevokedTokenError",
    "UserInactiveError",
    "UserNotFoundError",
]
