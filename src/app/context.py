"""Request context for user information."""

from contextvars import ContextVar
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestContext:
    """Immutable request context holding user information."""

    user_id: UUID
    firebase_uid: str
    email: str
    full_name: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    phone: str | None = None
    cpf: str | None = None
    correlation_id: str | None = None

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles

    def has_any_role(self, roles: list[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(role in self.roles for role in roles)

    def has_all_roles(self, roles: list[str]) -> bool:
        """Check if user has all of the specified roles."""
        return all(role in self.roles for role in roles)

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: list[str]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(permission in self.permissions for permission in permissions)

    def has_all_permissions(self, permissions: list[str]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(permission in self.permissions for permission in permissions)


# Context variable to hold request context
_request_context: ContextVar[RequestContext | None] = ContextVar(
    "request_context", default=None
)


def get_request_context() -> RequestContext | None:
    """Get current request context."""
    return _request_context.get()


def set_request_context(context: RequestContext) -> None:
    """Set current request context."""
    _request_context.set(context)


def clear_request_context() -> None:
    """Clear current request context."""
    _request_context.set(None)


def get_current_user_id() -> UUID | None:
    """Get current user ID from context."""
    context = get_request_context()
    return context.user_id if context else None
