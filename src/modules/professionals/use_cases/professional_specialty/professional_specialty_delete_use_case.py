"""Use case for soft-deleting a professional specialty."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
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
    ) -> None:
        """Soft delete a professional specialty."""
        professional_specialty = await self.repository.get_by_id_for_qualification(
            professional_specialty_id, qualification_id
        )
        if professional_specialty is None:
            raise NotFoundError(
                resource="ProfessionalSpecialty",
                identifier=str(professional_specialty_id),
            )

        await self.repository.soft_delete(professional_specialty_id)
