"""User module exceptions."""

from typing import Any

from src.app.constants.error_codes import UserErrorCodes
from src.app.exceptions import AppException
from src.app.i18n import UserMessages, get_message


class UserException(AppException):
    """Base exception for user module errors."""

    def __init__(
        self,
        message: str,
        code: str = UserErrorCodes.USER_NOT_FOUND,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


# =============================================================================
# User Errors
# =============================================================================


class UserNotFoundError(UserException):
    """User not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.USER_NOT_FOUND),
            code=UserErrorCodes.USER_NOT_FOUND,
            status_code=404,
            details=details,
        )


class UserAlreadyMemberError(UserException):
    """User is already a member of the organization."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.USER_ALREADY_MEMBER),
            code=UserErrorCodes.USER_ALREADY_MEMBER,
            status_code=409,
            details=details,
        )


class UserNotMemberError(UserException):
    """User is not a member of the organization."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.USER_NOT_MEMBER),
            code=UserErrorCodes.USER_NOT_MEMBER,
            status_code=404,
            details=details,
        )


# =============================================================================
# Invitation Errors
# =============================================================================


class InvitationAlreadySentError(UserException):
    """Invitation already sent to this email."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.INVITATION_ALREADY_SENT),
            code=UserErrorCodes.INVITATION_ALREADY_SENT,
            status_code=409,
            details=details,
        )


class InvitationNotFoundError(UserException):
    """Invitation not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.INVITATION_NOT_FOUND),
            code=UserErrorCodes.INVITATION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class InvitationExpiredError(UserException):
    """Invitation has expired."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.INVITATION_EXPIRED),
            code=UserErrorCodes.INVITATION_EXPIRED,
            status_code=410,
            details=details,
        )


class InvitationAlreadyAcceptedError(UserException):
    """Invitation has already been accepted."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.INVITATION_ALREADY_ACCEPTED),
            code=UserErrorCodes.INVITATION_ALREADY_ACCEPTED,
            status_code=409,
            details=details,
        )


class InvitationInvalidTokenError(UserException):
    """Invalid invitation token."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.INVITATION_INVALID_TOKEN),
            code=UserErrorCodes.INVITATION_INVALID_TOKEN,
            status_code=400,
            details=details,
        )


# =============================================================================
# Membership Errors
# =============================================================================


class MembershipNotFoundError(UserException):
    """Membership not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.MEMBERSHIP_NOT_FOUND),
            code=UserErrorCodes.MEMBERSHIP_NOT_FOUND,
            status_code=404,
            details=details,
        )


class CannotRemoveOwnerError(UserException):
    """Cannot remove the organization owner."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.CANNOT_REMOVE_OWNER),
            code=UserErrorCodes.CANNOT_REMOVE_OWNER,
            status_code=403,
            details=details,
        )


class CannotRemoveSelfError(UserException):
    """Cannot remove yourself from the organization."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.CANNOT_REMOVE_SELF),
            code=UserErrorCodes.CANNOT_REMOVE_SELF,
            status_code=403,
            details=details,
        )


# =============================================================================
# Role Errors
# =============================================================================


class RoleNotFoundError(UserException):
    """Role not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.ROLE_NOT_FOUND),
            code=UserErrorCodes.ROLE_NOT_FOUND,
            status_code=404,
            details=details,
        )


class InvalidRoleError(UserException):
    """Invalid role for this operation."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(UserMessages.INVALID_ROLE),
            code=UserErrorCodes.INVALID_ROLE,
            status_code=400,
            details=details,
        )
