"""Request context for multi-tenancy and user information."""

from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestContext:
    """Immutable request context holding user and tenant information."""

    user_id: UUID
    tenant_id: UUID
    roles: list[str]
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


def get_current_tenant_id() -> UUID | None:
    """Get current tenant ID from context."""
    context = get_request_context()
    return context.tenant_id if context else None


def get_current_user_id() -> UUID | None:
    """Get current user ID from context."""
    context = get_request_context()
    return context.user_id if context else None
