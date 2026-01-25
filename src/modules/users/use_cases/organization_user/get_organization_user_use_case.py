"""Use case for getting a single organization user (membership)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import MembershipNotFoundError
from src.modules.users.domain.schemas import OrganizationUserResponse
from src.modules.users.infrastructure.repositories import (
    OrganizationMembershipRepository,
)


class GetOrganizationUserUseCase:
    """
    Use case for getting a single user in an organization.

    Returns the membership details including user info and role.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationMembershipRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        membership_id: UUID,
    ) -> OrganizationUserResponse:
        """
        Get a single organization user by membership ID.

        Args:
            organization_id: The organization ID (for scope validation)
            membership_id: The membership ID to retrieve

        Returns:
            Organization user details

        Raises:
            MembershipNotFoundError: If membership not found or doesn't belong to org
        """
        membership = await self.repository.get_by_id_for_organization(
            membership_id=membership_id,
            organization_id=organization_id,
        )

        if not membership:
            raise MembershipNotFoundError()

        return OrganizationUserResponse.from_membership(membership)
