"""Use case for deleting an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class DeleteOrganizationProfessionalUseCase:
    """
    Use case for soft-deleting a professional from an organization.

    The professional is not physically deleted but marked with a deleted_at timestamp.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
    ) -> None:
        """
        Soft delete a professional.

        Args:
            professional_id: The professional UUID to delete.
            organization_id: The organization UUID.

        Raises:
            NotFoundError: If professional not found in organization.
        """
        # Verify professional exists in organization
        professional = await self.repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise NotFoundError(
                resource="OrganizationProfessional",
                identifier=str(professional_id),
            )

        # Soft delete
        await self.repository.soft_delete(professional_id)
