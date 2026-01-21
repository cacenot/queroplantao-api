"""Use case for retrieving a professional specialty."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalSpecialty
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalSpecialtyRepository,
)


class GetProfessionalSpecialtyUseCase:
    """Use case for retrieving a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_specialty_id: UUID,
        qualification_id: UUID,
    ) -> ProfessionalSpecialty:
        """Get a professional specialty by ID with specialty data loaded."""
        professional_specialty = await self.repository.get_by_id_with_specialty(
            professional_specialty_id, qualification_id
        )
        if professional_specialty is None:
            raise NotFoundError(
                resource="ProfessionalSpecialty",
                identifier=str(professional_specialty_id),
            )

        return professional_specialty
