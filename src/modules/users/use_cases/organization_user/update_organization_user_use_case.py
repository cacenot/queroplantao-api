"""Use case for updating an organization user's membership."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import MembershipNotFoundError, RoleNotFoundError
from src.modules.users.domain.schemas import (
    OrganizationUserResponse,
    OrganizationUserUpdate,
)
from src.modules.users.infrastructure.repositories import (
    OrganizationMembershipRepository,
    RoleRepository,
)


class UpdateOrganizationUserUseCase:
    """
    Use case for updating a user's membership in an organization.

    Supports updating role and active status.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.membership_repository = OrganizationMembershipRepository(session)
        self.role_repository = RoleRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        membership_id: UUID,
        data: OrganizationUserUpdate,
        updated_by: UUID,
    ) -> OrganizationUserResponse:
        """
        Update a user's membership.

        Args:
            organization_id: The organization ID (for scope validation)
            membership_id: The membership to update
            data: Update data (role_id, is_active)
            updated_by: User making the update

        Returns:
            Updated membership

        Raises:
            MembershipNotFoundError: If membership not found
            RoleNotFoundError: If specified role doesn't exist
        """
        # Get existing membership
        membership = await self.membership_repository.get_by_id_for_organization(
            membership_id=membership_id,
            organization_id=organization_id,
        )

        if not membership:
            raise MembershipNotFoundError()

        # Update role if provided
        if data.role_id is not None:
            role = await self.role_repository.get_by_id(data.role_id)
            if not role:
                raise RoleNotFoundError()

            membership = await self.membership_repository.update_role(
                membership_id=membership_id,
                new_role_id=data.role_id,
                updated_by=updated_by,
            )

        # Update active status if provided
        if data.is_active is not None:
            membership.is_active = data.is_active
            membership.updated_by = updated_by

        await self.session.commit()
        await self.session.refresh(
            membership, attribute_names=["user", "role", "organization"]
        )

        return OrganizationUserResponse.from_membership(membership)
