"""Use case for updating a professional specialty."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import SpecialtyNotFoundError
from src.modules.professionals.domain.models import ProfessionalSpecialty
from src.modules.professionals.domain.schemas import ProfessionalSpecialtyUpdate
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalSpecialtyRepository,
)


class UpdateProfessionalSpecialtyUseCase:
    """Use case for updating a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_specialty_id: UUID,
        qualification_id: UUID,
        data: ProfessionalSpecialtyUpdate,
        organization_id: UUID | None = None,
        professional_id: UUID | None = None,
        updated_by: UUID | None = None,
    ) -> ProfessionalSpecialty:
        """
        Update an existing professional specialty (PATCH semantics).

        Args:
            professional_specialty_id: The specialty link UUID to update.
            qualification_id: The qualification UUID.
            data: The partial update data.
            organization_id: The organization UUID (unused, for API consistency).
            professional_id: The professional UUID (unused, for API consistency).
            updated_by: UUID of the user updating this record (unused, for future audit).
        """
        professional_specialty = await self.repository.get_by_id_for_qualification(
            professional_specialty_id, qualification_id
        )
        if professional_specialty is None:
            raise SpecialtyNotFoundError()

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(professional_specialty, field, value)

        return await self.repository.update(professional_specialty)
