"""Organization-related exceptions."""

from typing import Any

from src.app.constants.error_codes import OrganizationErrorCodes
from src.app.exceptions import AppException


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
        message: str = "Organization ID is required",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.MISSING_ORGANIZATION_ID,
            status_code=400,
            details=details,
        )


class InvalidOrganizationIdError(OrganizationException):
    """Organization ID is not a valid UUID."""

    def __init__(
        self,
        message: str = "Organization ID must be a valid UUID",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.INVALID_ORGANIZATION_ID,
            status_code=400,
            details=details,
        )


class OrganizationNotFoundError(OrganizationException):
    """Organization not found in database."""

    def __init__(
        self,
        message: str = "Organization not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.ORGANIZATION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class OrganizationInactiveError(OrganizationException):
    """Organization is inactive."""

    def __init__(
        self,
        message: str = "Organization is inactive",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.ORGANIZATION_INACTIVE,
            status_code=403,
            details=details,
        )


class UserNotMemberError(OrganizationException):
    """User is not a member of the organization."""

    def __init__(
        self,
        message: str = "User is not a member of this organization",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.USER_NOT_MEMBER,
            status_code=403,
            details=details,
        )


class MembershipInactiveError(OrganizationException):
    """User's membership in the organization is inactive."""

    def __init__(
        self,
        message: str = "Membership in this organization is inactive",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.MEMBERSHIP_INACTIVE,
            status_code=403,
            details=details,
        )


class MembershipPendingError(OrganizationException):
    """User's membership invitation is pending acceptance."""

    def __init__(
        self,
        message: str = "Membership invitation is pending acceptance",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.MEMBERSHIP_PENDING,
            status_code=403,
            details=details,
        )


class MembershipExpiredError(OrganizationException):
    """User's membership has expired."""

    def __init__(
        self,
        message: str = "Membership has expired",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.MEMBERSHIP_EXPIRED,
            status_code=403,
            details=details,
        )


class InvalidChildOrganizationIdError(OrganizationException):
    """Child organization ID is not a valid UUID."""

    def __init__(
        self,
        message: str = "Child organization ID must be a valid UUID",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.INVALID_CHILD_ORGANIZATION_ID,
            status_code=400,
            details=details,
        )


class ChildOrganizationNotFoundError(OrganizationException):
    """Child organization not found in database."""

    def __init__(
        self,
        message: str = "Child organization not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.CHILD_ORGANIZATION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class ChildOrganizationInactiveError(OrganizationException):
    """Child organization is inactive."""

    def __init__(
        self,
        message: str = "Child organization is inactive",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.CHILD_ORGANIZATION_INACTIVE,
            status_code=403,
            details=details,
        )


class ChildNotAllowedError(OrganizationException):
    """Organization does not allow child organizations."""

    def __init__(
        self,
        message: str = "This organization does not support child organizations",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.CHILD_NOT_ALLOWED,
            status_code=400,
            details=details,
        )


class NotChildOfParentError(OrganizationException):
    """Child organization is not a child of the specified parent."""

    def __init__(
        self,
        message: str = "The specified organization is not a child of the parent organization",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=OrganizationErrorCodes.NOT_CHILD_OF_PARENT,
            status_code=400,
            details=details,
        )
