"""Use case for soft-deleting a professional specialty."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import SpecialtyNotFoundError
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalSpecialtyRepository,
)


class DeleteProfessionalSpecialtyUseCase:
    """Use case for soft-deleting a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_specialty_id: UUID,
        qualification_id: UUID,
        organization_id: UUID | None = None,
        professional_id: UUID | None = None,
        deleted_by: UUID | None = None,
    ) -> None:
        """
        Soft delete a professional specialty.

        Args:
            professional_specialty_id: The specialty link UUID to delete.
            qualification_id: The qualification UUID.
            organization_id: The organization UUID (unused, for API consistency).
            professional_id: The professional UUID (unused, for API consistency).
            deleted_by: UUID of the user deleting this record (unused, for future audit).
        """
        professional_specialty = await self.repository.get_by_id_for_qualification(
            professional_specialty_id, qualification_id
        )
        if professional_specialty is None:
            raise SpecialtyNotFoundError()

        await self.repository.delete(professional_specialty_id)
