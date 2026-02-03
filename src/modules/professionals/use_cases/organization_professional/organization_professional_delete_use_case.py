"""Use case for deleting an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ProfessionalNotFoundError
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class DeleteOrganizationProfessionalUseCase:
    """
    Use case for soft-deleting a professional from an organization family.

    The professional is not physically deleted but marked with a deleted_at timestamp.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
    ) -> None:
        """
        Soft delete a professional.

        Args:
            professional_id: The professional UUID to delete.
            organization_id: The organization UUID.
            family_org_ids: List of all organization IDs in the family.

        Raises:
            ProfessionalNotFoundError: If professional not found in organization family.
        """
        # Verify professional exists in organization family
        professional = await self.repository.get_by_id_for_organization(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # Soft delete
        await self.repository.delete(professional_id)
