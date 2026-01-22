"""Use case for updating a professional education record."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalEducation
from src.modules.professionals.domain.schemas import ProfessionalEducationUpdate
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalEducationRepository,
)


class UpdateProfessionalEducationUseCase:
    """Use case for updating a professional education record."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)

    async def execute(
        self,
        education_id: UUID,
        qualification_id: UUID,
        data: ProfessionalEducationUpdate,
        organization_id: UUID | None = None,
        professional_id: UUID | None = None,
        updated_by: UUID | None = None,
    ) -> ProfessionalEducation:
        """
        Update an existing education record (PATCH semantics).

        Args:
            education_id: The education UUID to update.
            qualification_id: The qualification UUID.
            data: The partial update data.
            organization_id: The organization UUID (unused, for API consistency).
            professional_id: The professional UUID (unused, for API consistency).
            updated_by: UUID of the user updating this record (unused, for future audit).
        """
        education = await self.repository.get_by_id_for_qualification(
            education_id, qualification_id
        )
        if education is None:
            raise NotFoundError(
                resource="ProfessionalEducation",
                identifier=str(education_id),
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(education, field, value)

        return await self.repository.update(education)
