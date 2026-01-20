"""Authentication-related exceptions."""

from typing import Any

from src.app.constants.error_codes import AuthErrorCodes
from src.app.exceptions import AppException


class AuthException(AppException):
    """Base exception for authentication errors."""

    def __init__(
        self,
        message: str,
        code: str = AuthErrorCodes.INVALID_TOKEN,
        status_code: int = 401,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


class MissingTokenError(AuthException):
    """Token not provided in request."""

    def __init__(
        self,
        message: str = "Authorization token is required",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.MISSING_TOKEN,
            status_code=401,
            details=details,
        )


class InvalidTokenError(AuthException):
    """Token is invalid or malformed."""

    def __init__(
        self,
        message: str = "Invalid authentication token",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.INVALID_TOKEN,
            status_code=401,
            details=details,
        )


class ExpiredTokenError(AuthException):
    """Token has expired."""

    def __init__(
        self,
        message: str = "Authentication token has expired",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.EXPIRED_TOKEN,
            status_code=401,
            details=details,
        )


class RevokedTokenError(AuthException):
    """Token has been revoked."""

    def __init__(
        self,
        message: str = "Authentication token has been revoked",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.REVOKED_TOKEN,
            status_code=401,
            details=details,
        )


class FirebaseAuthError(AuthException):
    """Firebase authentication error."""

    def __init__(
        self,
        message: str = "Firebase authentication failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.FIREBASE_ERROR,
            status_code=401,
            details=details,
        )


class FirebaseInitError(AuthException):
    """Firebase initialization error."""

    def __init__(
        self,
        message: str = "Firebase service initialization failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.FIREBASE_INIT_ERROR,
            status_code=500,
            details=details,
        )


class UserNotFoundError(AuthException):
    """User not found in database."""

    def __init__(
        self,
        message: str = "User not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.USER_NOT_FOUND,
            status_code=401,
            details=details,
        )


class UserInactiveError(AuthException):
    """User account is inactive."""

    def __init__(
        self,
        message: str = "User account is inactive",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.USER_INACTIVE,
            status_code=403,
            details=details,
        )


class CacheError(AuthException):
    """Cache operation error."""

    def __init__(
        self,
        message: str = "Cache operation failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=AuthErrorCodes.CACHE_ERROR,
            status_code=500,
            details=details,
        )
