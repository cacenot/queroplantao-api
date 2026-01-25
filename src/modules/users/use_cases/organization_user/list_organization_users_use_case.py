"""Use case for listing organization users (memberships)."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organizations.domain.models.organization_membership import (
    OrganizationMembership,
)
from src.modules.users.domain.schemas import (
    OrganizationUserListItem,
    OrganizationUserResponse,
)
from src.modules.users.infrastructure.filters import (
    OrganizationUserFilter,
    OrganizationUserSorting,
)
from src.modules.users.infrastructure.repositories import (
    OrganizationMembershipRepository,
)


class ListOrganizationUsersUseCase:
    """
    Use case for listing users in an organization.

    Returns paginated list of organization members with their roles.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationMembershipRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        filters: OrganizationUserFilter | None = None,
        sorting: OrganizationUserSorting | None = None,
        include_pending: bool = True,
    ) -> PaginatedResponse[OrganizationUserResponse]:
        """
        List all users in an organization.

        Args:
            organization_id: The organization to list users for
            pagination: Pagination parameters
            filters: Optional filters (search, role, is_active)
            sorting: Optional sorting
            include_pending: Whether to include pending invitations

        Returns:
            Paginated list of organization users
        """
        result = await self.repository.list_for_organization(
            organization_id=organization_id,
            pagination=pagination,
            filters=filters,
            sorting=sorting,
            include_pending=include_pending,
        )

        # Transform to response schema
        items = [OrganizationUserResponse.from_membership(m) for m in result.items]

        return PaginatedResponse(
            items=items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )

    async def execute_summary(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        filters: OrganizationUserFilter | None = None,
        sorting: OrganizationUserSorting | None = None,
        include_pending: bool = True,
    ) -> PaginatedResponse[OrganizationUserListItem]:
        """
        List users with simplified data.

        Args:
            organization_id: The organization to list users for
            pagination: Pagination parameters
            filters: Optional filters
            sorting: Optional sorting
            include_pending: Whether to include pending invitations

        Returns:
            Paginated list of simplified user data
        """
        result = await self.repository.list_for_organization(
            organization_id=organization_id,
            pagination=pagination,
            filters=filters,
            sorting=sorting,
            include_pending=include_pending,
        )

        items = [OrganizationUserListItem.from_membership(m) for m in result.items]

        return PaginatedResponse(
            items=items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )
