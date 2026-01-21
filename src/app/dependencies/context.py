"""Context dependencies for FastAPI routes."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.context import RequestContext, get_request_context
from src.app.exceptions import AuthenticationError, AuthorizationError


class ValidatedContext(RequestContext):
    """
    RequestContext wrapper that guarantees the user is authenticated.

    Inherits all methods from RequestContext and adds convenience properties
    for accessing commonly used values in route handlers.
    """

    @property
    def user(self) -> UUID:
        """Alias for user_id for cleaner access."""
        return self.user_id

    @property
    def organization(self) -> UUID:
        """
        Get the active organization ID.

        Returns child_organization_id if set, otherwise organization_id.
        Raises AuthorizationError if no organization context is set.
        """
        org_id = self.active_organization_id
        if org_id is None:
            raise AuthorizationError(
                message="Organization context required. Set X-Organization-Id header."
            )
        return org_id

    @classmethod
    def from_request_context(cls, ctx: RequestContext) -> "ValidatedContext":
        """Create a ValidatedContext from a RequestContext."""
        return cls(
            user_id=ctx.user_id,
            firebase_uid=ctx.firebase_uid,
            email=ctx.email,
            full_name=ctx.full_name,
            roles=ctx.roles,
            permissions=ctx.permissions,
            phone=ctx.phone,
            cpf=ctx.cpf,
            correlation_id=ctx.correlation_id,
            organization_id=ctx.organization_id,
            organization_name=ctx.organization_name,
            organization_role=ctx.organization_role,
            child_organization_id=ctx.child_organization_id,
            child_organization_name=ctx.child_organization_name,
        )


# HTTPBearer for OpenAPI documentation (middleware handles actual auth)
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="JWT token issued by BFF after Firebase authentication",
    auto_error=False,  # Middleware handles auth, this is for docs only
)


def get_validated_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> ValidatedContext:
    """
    Get the current request context, validating that user is authenticated.

    The HTTPBearer dependency is used for OpenAPI/Swagger documentation.
    Actual authentication is handled by the Firebase middleware.

    Raises:
        AuthenticationError: If no context exists (user not authenticated).
    """
    context = get_request_context()
    if context is None:
        raise AuthenticationError(message="Authentication required")
    return ValidatedContext.from_request_context(context)


def get_organization_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> ValidatedContext:
    """
    Get the current request context, validating organization context exists.

    Raises:
        AuthenticationError: If no context exists (user not authenticated).
        AuthorizationError: If no organization context is set.
    """
    context = get_validated_context(credentials)
    if not context.has_organization():
        raise AuthorizationError(
            message="Organization context required. Set X-Organization-Id header."
        )
    return context


# Type aliases for cleaner route signatures
CurrentContext = Annotated[ValidatedContext, Depends(get_validated_context)]
OrganizationContext = Annotated[ValidatedContext, Depends(get_organization_context)]
