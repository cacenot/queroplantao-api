"""Use case for creating a professional education record."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalEducation
from src.modules.professionals.domain.schemas import ProfessionalEducationCreate
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalEducationRepository,
    ProfessionalQualificationRepository,
)


class CreateProfessionalEducationUseCase:
    """Use case for creating a professional education record."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        data: ProfessionalEducationCreate,
    ) -> ProfessionalEducation:
        """
        Create a new education record for a qualification.

        Validates:
        - Qualification exists in organization
        """
        # Verify qualification exists
        qualification = await self.qualification_repository.get_by_id_for_organization(
            qualification_id, organization_id
        )
        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        education = ProfessionalEducation(
            qualification_id=qualification_id,
            **data.model_dump(),
        )

        return await self.repository.create(education)
