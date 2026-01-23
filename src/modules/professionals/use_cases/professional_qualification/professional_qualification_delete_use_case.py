"""Use case for soft-deleting a professional qualification."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import QualificationNotFoundError
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
)


class DeleteProfessionalQualificationUseCase:
    """Use case for soft-deleting a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        professional_id: UUID | None = None,
        deleted_by: UUID | None = None,
    ) -> None:
        """
        Soft delete a qualification.

        Args:
            qualification_id: The qualification UUID to delete.
            organization_id: The organization UUID.
            professional_id: The professional UUID (unused, for API consistency).
            deleted_by: UUID of the user deleting this record (unused, for future audit).
        """
        qualification = await self.repository.get_by_id_for_organization(
            qualification_id, organization_id
        )
        if qualification is None:
            raise QualificationNotFoundError()

        await self.repository.soft_delete(qualification_id)
