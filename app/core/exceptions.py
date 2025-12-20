"""Custom application exceptions."""

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Authentication failed."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationError(AppException):
    """Authorization failed - insufficient permissions."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ConflictError(AppException):
    """Resource conflict - already exists or invalid state."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class TenantError(AppException):
    """Tenant-related error."""

    def __init__(
        self,
        message: str = "Tenant error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="TENANT_ERROR",
            status_code=400,
            details=details,
        )
