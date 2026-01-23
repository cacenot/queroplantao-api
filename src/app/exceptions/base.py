"""Custom application exceptions."""

from typing import Any

from src.app.i18n import AuthMessages, ResourceMessages, get_message, translate_resource


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
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.AUTHENTICATION_FAILED),
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationError(AppException):
    """Authorization failed - insufficient permissions."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(AuthMessages.INSUFFICIENT_PERMISSIONS),
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
        # Translate the resource name to the current locale
        translated_resource = translate_resource(resource)

        if identifier:
            message = get_message(
                ResourceMessages.NOT_FOUND_WITH_ID,
                resource=translated_resource,
                identifier=identifier,
            )
        else:
            message = get_message(
                ResourceMessages.NOT_FOUND, resource=translated_resource
            )
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
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ResourceMessages.CONFLICT),
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ResourceMessages.VALIDATION_ERROR),
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )
