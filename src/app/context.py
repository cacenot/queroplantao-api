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

    # Organization context (set by OrganizationIdentityMiddleware)
    organization_id: UUID | None = None
    organization_name: str | None = None
    organization_role: str | None = None
    organization_role_name: str | None = None
    child_organization_id: UUID | None = None
    child_organization_name: str | None = None
    parent_organization_id: UUID | None = None

    # Family organization IDs for hierarchical data scope
    # Contains all org IDs in the family (parent + children/siblings)
    # Used for queries with DataScopePolicy.FAMILY
    family_org_ids: tuple[UUID, ...] = field(default_factory=tuple)

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

    def has_organization(self) -> bool:
        """Check if request has an organization context."""
        return self.organization_id is not None

    def has_child_organization(self) -> bool:
        """Check if request has a child organization context."""
        return self.child_organization_id is not None

    def has_org_role(self, role: str) -> bool:
        """Check if user has a specific role in the current organization."""
        return self.organization_role == role

    def is_org_owner(self) -> bool:
        """Check if user is owner of the current organization."""
        return self.organization_role == "ORG_OWNER"

    def is_org_admin(self) -> bool:
        """Check if user is admin (or owner) of the current organization."""
        return self.organization_role in ("ORG_OWNER", "ORG_ADMIN")

    def is_org_manager(self) -> bool:
        """Check if user can manage (owner, admin, or manager)."""
        return self.organization_role in ("ORG_OWNER", "ORG_ADMIN", "ORG_MANAGER")

    def is_org_scheduler(self) -> bool:
        """Check if user can schedule (owner, admin, manager, or scheduler)."""
        return self.organization_role in (
            "ORG_OWNER",
            "ORG_ADMIN",
            "ORG_MANAGER",
            "ORG_SCHEDULER",
        )

    @property
    def active_organization_id(self) -> UUID | None:
        """
        Get the active organization ID.

        Returns child_organization_id if set, otherwise organization_id.
        This represents the "working" organization context.
        """
        return self.child_organization_id or self.organization_id


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
