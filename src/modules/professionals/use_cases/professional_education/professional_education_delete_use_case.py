"""Use case for soft-deleting a professional education record."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalEducationRepository,
)


class DeleteProfessionalEducationUseCase:
    """Use case for soft-deleting a professional education record."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)

    async def execute(
        self,
        education_id: UUID,
        qualification_id: UUID,
        organization_id: UUID | None = None,
        professional_id: UUID | None = None,
        deleted_by: UUID | None = None,
    ) -> None:
        """
        Soft delete an education record.

        Args:
            education_id: The education UUID to delete.
            qualification_id: The qualification UUID.
            organization_id: The organization UUID (unused, for API consistency).
            professional_id: The professional UUID (unused, for API consistency).
            deleted_by: UUID of the user deleting this record (unused, for future audit).
        """
        education = await self.repository.get_by_id_for_qualification(
            education_id, qualification_id
        )
        if education is None:
            raise NotFoundError(
                resource="ProfessionalEducation",
                identifier=str(education_id),
            )

        await self.repository.delete(education_id)
