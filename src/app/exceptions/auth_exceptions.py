"""Authentication-related exceptions."""

from typing import Any

from src.app.constants.error_codes import AuthErrorCodes
from src.app.exceptions import AppException
from src.app.i18n import AuthMessages, get_message


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
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.MISSING_TOKEN),
            code=AuthErrorCodes.MISSING_TOKEN,
            status_code=401,
            details=details,
        )


class InvalidTokenError(AuthException):
    """Token is invalid or malformed."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.INVALID_TOKEN),
            code=AuthErrorCodes.INVALID_TOKEN,
            status_code=401,
            details=details,
        )


class ExpiredTokenError(AuthException):
    """Token has expired."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.EXPIRED_TOKEN),
            code=AuthErrorCodes.EXPIRED_TOKEN,
            status_code=401,
            details=details,
        )


class RevokedTokenError(AuthException):
    """Token has been revoked."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.REVOKED_TOKEN),
            code=AuthErrorCodes.REVOKED_TOKEN,
            status_code=401,
            details=details,
        )


class FirebaseAuthError(AuthException):
    """Firebase authentication error."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.FIREBASE_ERROR),
            code=AuthErrorCodes.FIREBASE_ERROR,
            status_code=401,
            details=details,
        )


class FirebaseInitError(AuthException):
    """Firebase initialization error."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.FIREBASE_INIT_ERROR),
            code=AuthErrorCodes.FIREBASE_INIT_ERROR,
            status_code=500,
            details=details,
        )


class UserNotFoundError(AuthException):
    """User not found in database."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.USER_NOT_FOUND),
            code=AuthErrorCodes.USER_NOT_FOUND,
            status_code=401,
            details=details,
        )


class UserInactiveError(AuthException):
    """User account is inactive."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.USER_INACTIVE),
            code=AuthErrorCodes.USER_INACTIVE,
            status_code=403,
            details=details,
        )


class CacheError(AuthException):
    """Cache operation error."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.CACHE_ERROR),
            code=AuthErrorCodes.CACHE_ERROR,
            status_code=500,
            details=details,
        )
