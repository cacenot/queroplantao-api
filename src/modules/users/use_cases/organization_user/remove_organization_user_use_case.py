"""Use case for removing a user from an organization."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    CannotRemoveOwnerError,
    CannotRemoveSelfError,
    MembershipNotFoundError,
)
from src.modules.users.infrastructure.repositories import (
    OrganizationMembershipRepository,
)


class RemoveOrganizationUserUseCase:
    """
    Use case for removing a user from an organization.

    Deactivates all memberships for the user in the organization.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationMembershipRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        membership_id: UUID,
        removed_by: UUID,
    ) -> None:
        """
        Remove a user from an organization.

        Args:
            organization_id: The organization ID (for scope validation)
            membership_id: The membership to remove
            removed_by: User performing the removal

        Raises:
            MembershipNotFoundError: If membership not found
            CannotRemoveSelfError: If trying to remove yourself
            CannotRemoveOwnerError: If trying to remove the org owner
        """
        # Get existing membership
        membership = await self.repository.get_by_id_for_organization(
            membership_id=membership_id,
            organization_id=organization_id,
        )

        if not membership:
            raise MembershipNotFoundError()

        # Check if trying to remove self
        if membership.user_id == removed_by:
            raise CannotRemoveSelfError()

        # Check if trying to remove owner (role code = 'owner' or 'org_owner')
        if membership.role and membership.role.code in (
            "owner",
            "org_owner",
            "ORG_OWNER",
        ):
            raise CannotRemoveOwnerError()

        # Deactivate all memberships for this user in the organization
        await self.repository.deactivate_all_for_user(
            user_id=membership.user_id,
            organization_id=organization_id,
            deactivated_by=removed_by,
        )

        await self.session.commit()
