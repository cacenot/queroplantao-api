"""Organization-related exceptions."""

from typing import Any

from src.app.constants.error_codes import OrganizationErrorCodes
from src.app.exceptions import AppException
from src.app.i18n import OrganizationMessages, get_message


class OrganizationException(AppException):
    """Base exception for organization errors."""

    def __init__(
        self,
        message: str,
        code: str = OrganizationErrorCodes.ORGANIZATION_NOT_FOUND,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


class MissingOrganizationIdError(OrganizationException):
    """Organization ID not provided in request."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.MISSING_ID),
            code=OrganizationErrorCodes.MISSING_ORGANIZATION_ID,
            status_code=400,
            details=details,
        )


class InvalidOrganizationIdError(OrganizationException):
    """Organization ID is not a valid UUID."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.INVALID_ID),
            code=OrganizationErrorCodes.INVALID_ORGANIZATION_ID,
            status_code=400,
            details=details,
        )


class OrganizationNotFoundError(OrganizationException):
    """Organization not found in database."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.NOT_FOUND),
            code=OrganizationErrorCodes.ORGANIZATION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class OrganizationInactiveError(OrganizationException):
    """Organization is inactive."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.INACTIVE),
            code=OrganizationErrorCodes.ORGANIZATION_INACTIVE,
            status_code=403,
            details=details,
        )


class UserNotMemberError(OrganizationException):
    """User is not a member of the organization."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.USER_NOT_MEMBER),
            code=OrganizationErrorCodes.USER_NOT_MEMBER,
            status_code=403,
            details=details,
        )


class MembershipInactiveError(OrganizationException):
    """User's membership in the organization is inactive."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.MEMBERSHIP_INACTIVE),
            code=OrganizationErrorCodes.MEMBERSHIP_INACTIVE,
            status_code=403,
            details=details,
        )


class MembershipPendingError(OrganizationException):
    """User's membership invitation is pending acceptance."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.MEMBERSHIP_PENDING),
            code=OrganizationErrorCodes.MEMBERSHIP_PENDING,
            status_code=403,
            details=details,
        )


class MembershipExpiredError(OrganizationException):
    """User's membership has expired."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.MEMBERSHIP_EXPIRED),
            code=OrganizationErrorCodes.MEMBERSHIP_EXPIRED,
            status_code=403,
            details=details,
        )


class InvalidChildOrganizationIdError(OrganizationException):
    """Child organization ID is not a valid UUID."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.INVALID_CHILD_ID),
            code=OrganizationErrorCodes.INVALID_CHILD_ORGANIZATION_ID,
            status_code=400,
            details=details,
        )


class ChildOrganizationNotFoundError(OrganizationException):
    """Child organization not found in database."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.CHILD_NOT_FOUND),
            code=OrganizationErrorCodes.CHILD_ORGANIZATION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class ChildOrganizationInactiveError(OrganizationException):
    """Child organization is inactive."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.CHILD_INACTIVE),
            code=OrganizationErrorCodes.CHILD_ORGANIZATION_INACTIVE,
            status_code=403,
            details=details,
        )


class ChildNotAllowedError(OrganizationException):
    """Organization does not allow child organizations."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.CHILD_NOT_ALLOWED),
            code=OrganizationErrorCodes.CHILD_NOT_ALLOWED,
            status_code=400,
            details=details,
        )


class NotChildOfParentError(OrganizationException):
    """Child organization is not a child of the specified parent."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(OrganizationMessages.NOT_CHILD_OF_PARENT),
            code=OrganizationErrorCodes.NOT_CHILD_OF_PARENT,
            status_code=400,
            details=details,
        )
