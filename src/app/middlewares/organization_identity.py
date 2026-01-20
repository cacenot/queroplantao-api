"""Organization identity middleware."""

from dataclasses import replace
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.app.config import Settings
from src.app.context import (
    get_request_context,
    set_request_context,
)
from src.app.dependencies import get_settings
from src.app.exceptions.organization_exceptions import (
    ChildNotAllowedError,
    ChildOrganizationInactiveError,
    ChildOrganizationNotFoundError,
    InvalidChildOrganizationIdError,
    InvalidOrganizationIdError,
    MissingOrganizationIdError,
    NotChildOfParentError,
    OrganizationException,
    OrganizationInactiveError,
    OrganizationNotFoundError,
    UserNotMemberError,
)
from src.app.logging import get_logger
from src.app.middlewares.constants import (
    CHILD_ORGANIZATION_ID_HEADER,
    DEFAULT_EXCLUDE_PATHS,
    ORGANIZATION_ID_HEADER,
)
from src.modules.organizations.infrastructure.repositories import OrganizationRepository
from src.shared.infrastructure.cache import RedisCache, get_redis_cache
from src.shared.infrastructure.database.connection import async_session_factory


logger = get_logger(__name__)


class OrganizationIdentityMiddleware(BaseHTTPMiddleware):
    """
    Organization identity middleware.

    Identifies the active organization from request headers,
    validates user membership, caches results in Redis,
    and updates RequestContext with organization data.

    Headers:
    - X-Organization-Id: Required organization UUID
    - X-Child-Organization-Id: Optional child organization UUID
      (only valid if parent org can have children)

    Flow:
    1. Check if path requires organization context
    2. Extract organization ID from header
    3. Check organization cache (Redis) - if hit, use cached data
    4. Look up organization in database
    5. Cache organization data with configured TTL
    6. Check membership cache (Redis) - if hit, use cached data
    7. Validate user is active member of organization
    8. Cache membership data with configured TTL
    9. If child org header present, validate child relationship
    10. Update RequestContext with organization data
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: set[str] | None = None,
        exclude_prefixes: tuple[str, ...] | None = None,
        require_organization: bool = True,
    ) -> None:
        """
        Initialize organization identity middleware.

        Args:
            app: ASGI application.
            exclude_paths: Exact paths to exclude from organization check.
            exclude_prefixes: Path prefixes to exclude.
            require_organization: If True, organization header is required
                                  for non-excluded paths. If False, organization
                                  is optional but validated if provided.
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or DEFAULT_EXCLUDE_PATHS
        self.exclude_prefixes = exclude_prefixes or ()
        self.require_organization = require_organization

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        """Process request with organization identification."""
        # Skip for excluded paths
        if self._should_skip(request.url.path):
            return await call_next(request)

        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        try:
            # Get current context (set by FirebaseAuthMiddleware)
            current_context = get_request_context()
            if not current_context:
                # No auth context means FirebaseAuthMiddleware didn't run
                # or user is not authenticated - just pass through
                return await call_next(request)

            # Extract organization ID from header
            org_id_str = request.headers.get(ORGANIZATION_ID_HEADER)

            # If organization not provided
            if not org_id_str:
                if self.require_organization:
                    raise MissingOrganizationIdError()
                # Organization is optional and not provided - pass through
                return await call_next(request)

            # Validate UUID format
            try:
                organization_id = UUID(org_id_str)
            except ValueError:
                raise InvalidOrganizationIdError(
                    details={"organization_id": org_id_str}
                )

            # Get services
            settings = get_settings()
            cache = get_redis_cache()

            # Get organization data (with cache)
            org_data = await self._get_organization_with_cache(
                organization_id=organization_id,
                cache=cache,
                settings=settings,
            )

            # Validate membership (with cache)
            membership_data = await self._get_membership_with_cache(
                user_id=current_context.user_id,
                organization_id=organization_id,
                cache=cache,
                settings=settings,
            )

            # Initialize child organization data
            child_org_data: dict | None = None

            # Check for child organization header
            child_org_id_str = request.headers.get(CHILD_ORGANIZATION_ID_HEADER)
            if child_org_id_str:
                # Validate parent can have children
                if not org_data["can_have_children"]:
                    raise ChildNotAllowedError(
                        details={"organization_id": str(organization_id)}
                    )

                # Validate UUID format
                try:
                    child_organization_id = UUID(child_org_id_str)
                except ValueError:
                    raise InvalidChildOrganizationIdError(
                        details={"child_organization_id": child_org_id_str}
                    )

                # Get child organization data (with cache)
                child_org_data = await self._get_organization_with_cache(
                    organization_id=child_organization_id,
                    cache=cache,
                    settings=settings,
                    is_child=True,
                )

                # Validate child relationship
                await self._validate_child_relationship(
                    child_id=child_organization_id,
                    parent_id=organization_id,
                )

            # Update context with organization data
            updated_context = replace(
                current_context,
                organization_id=organization_id,
                organization_name=org_data["name"],
                organization_role=membership_data["role_code"],
                child_organization_id=(
                    UUID(child_org_data["id"]) if child_org_data else None
                ),
                child_organization_name=(
                    child_org_data["name"] if child_org_data else None
                ),
            )
            set_request_context(updated_context)

            # Bind organization context to logs
            logger.bind(
                organization_id=str(organization_id),
                organization_role=membership_data["role_code"],
            )
            if child_org_data:
                logger.bind(child_organization_id=child_org_data["id"])

            # Process request
            response = await call_next(request)
            return response

        except OrganizationException as e:
            logger.warning(
                "organization_identity_failed",
                error_code=e.code,
                error_message=e.message,
            )
            return self._error_response(
                status_code=e.status_code,
                code=e.code,
                message=e.message,
                details=e.details,
            )
        except Exception as e:
            logger.exception("organization_identity_unexpected_error", error=str(e))
            return self._error_response(
                status_code=500,
                code="INTERNAL_ERROR",
                message="Organization identification failed due to internal error",
            )

    def _should_skip(self, path: str) -> bool:
        """Check if path should skip organization check."""
        if path in self.exclude_paths:
            return True

        for prefix in self.exclude_prefixes:
            if path.startswith(prefix):
                return True

        return False

    async def _get_organization_with_cache(
        self,
        organization_id: UUID,
        cache: RedisCache | None,
        settings: Settings,
        is_child: bool = False,
    ) -> dict:
        """
        Get organization data with caching.

        Args:
            organization_id: Organization UUID.
            cache: Redis cache instance (optional).
            settings: Application settings.
            is_child: Whether this is a child organization lookup.

        Returns:
            Dict with organization data.

        Raises:
            OrganizationNotFoundError: If organization not found.
            OrganizationInactiveError: If organization is inactive.
            ChildOrganizationNotFoundError: If child org not found.
            ChildOrganizationInactiveError: If child org is inactive.
        """
        org_id_str = str(organization_id)

        # Try cache first
        if cache:
            cache_key = cache.organization_cache_key(org_id_str)
            cached = await cache.get(cache_key)

            if cached:
                logger.debug(
                    "organization_cache_hit",
                    organization_id=org_id_str,
                    is_child=is_child,
                )
                # Validate cached org is still active
                if not cached.get("is_active", False):
                    if is_child:
                        raise ChildOrganizationInactiveError(
                            details={"child_organization_id": org_id_str}
                        )
                    raise OrganizationInactiveError(
                        details={"organization_id": org_id_str}
                    )
                return cached

        # Query database
        async with async_session_factory() as session:
            repo = OrganizationRepository(session)
            org = await repo.get_active_by_id(organization_id)

            if not org:
                # Check if org exists but is inactive
                inactive_org = await repo.get_by_id(organization_id)
                if inactive_org and inactive_org.deleted_at is None:
                    if is_child:
                        raise ChildOrganizationInactiveError(
                            details={"child_organization_id": org_id_str}
                        )
                    raise OrganizationInactiveError(
                        details={"organization_id": org_id_str}
                    )

                if is_child:
                    raise ChildOrganizationNotFoundError(
                        details={"child_organization_id": org_id_str}
                    )
                raise OrganizationNotFoundError(details={"organization_id": org_id_str})

            org_data = {
                "id": str(org.id),
                "name": org.name,
                "is_active": org.is_active,
                "parent_id": str(org.parent_id) if org.parent_id else None,
                "can_have_children": org.can_have_children(),
            }

        # Cache the result
        if cache:
            await cache.set(
                key=cache.organization_cache_key(org_id_str),
                value=org_data,
                ttl=settings.REDIS_ORG_CACHE_TTL,
            )
            logger.debug(
                "organization_cached",
                organization_id=org_id_str,
                ttl=settings.REDIS_ORG_CACHE_TTL,
            )

        return org_data

    async def _get_membership_with_cache(
        self,
        user_id: UUID,
        organization_id: UUID,
        cache: RedisCache | None,
        settings: Settings,
    ) -> dict:
        """
        Get user's organization membership with caching.

        Args:
            user_id: User UUID.
            organization_id: Organization UUID.
            cache: Redis cache instance (optional).
            settings: Application settings.

        Returns:
            Dict with membership data including role_code.

        Raises:
            UserNotMemberError: If user is not a member.
            MembershipInactiveError: If membership is inactive.
            MembershipPendingError: If membership is pending.
            MembershipExpiredError: If membership has expired.
        """
        user_id_str = str(user_id)
        org_id_str = str(organization_id)

        # Try cache first
        if cache:
            cache_key = cache.membership_cache_key(user_id_str, org_id_str)
            cached = await cache.get(cache_key)

            if cached:
                logger.debug(
                    "membership_cache_hit",
                    user_id=user_id_str,
                    organization_id=org_id_str,
                )
                return cached

        # Query database
        async with async_session_factory() as session:
            repo = OrganizationRepository(session)
            membership = await repo.get_user_membership(user_id, organization_id)

            if not membership:
                raise UserNotMemberError(
                    details={
                        "user_id": user_id_str,
                        "organization_id": org_id_str,
                    }
                )

            membership_data = {
                "membership_id": str(membership.id),
                "role_id": str(membership.role_id),
                "role_code": membership.role.code if membership.role else None,
                "is_active": membership.is_active,
            }

        # Cache the result
        if cache:
            await cache.set(
                key=cache.membership_cache_key(user_id_str, org_id_str),
                value=membership_data,
                ttl=settings.REDIS_MEMBERSHIP_CACHE_TTL,
            )
            logger.debug(
                "membership_cached",
                user_id=user_id_str,
                organization_id=org_id_str,
                ttl=settings.REDIS_MEMBERSHIP_CACHE_TTL,
            )

        return membership_data

    async def _validate_child_relationship(
        self,
        child_id: UUID,
        parent_id: UUID,
    ) -> None:
        """
        Validate that child organization is a child of parent.

        Args:
            child_id: Child organization UUID.
            parent_id: Parent organization UUID.

        Raises:
            NotChildOfParentError: If child is not a child of parent.
        """
        async with async_session_factory() as session:
            repo = OrganizationRepository(session)
            is_child = await repo.is_child_of_parent(child_id, parent_id)

            if not is_child:
                raise NotChildOfParentError(
                    details={
                        "child_organization_id": str(child_id),
                        "parent_organization_id": str(parent_id),
                    }
                )

    def _error_response(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> JSONResponse:
        """Create JSON error response."""
        return JSONResponse(
            status_code=status_code,
            content={
                "code": code,
                "message": message,
                "details": details or {},
            },
        )
