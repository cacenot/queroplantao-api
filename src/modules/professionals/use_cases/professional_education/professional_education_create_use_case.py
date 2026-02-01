"""Use case for creating a professional education record."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import QualificationNotFoundError
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
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
    ) -> ProfessionalEducation:
        """
        Create a new education record for a qualification.

        Validates:
        - Qualification exists in organization
        """
        # Verify qualification exists
        qualification = await self.qualification_repository.get_by_organization(
            id=qualification_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
        )
        if qualification is None:
            raise QualificationNotFoundError()

        education = ProfessionalEducation(
            organization_id=organization_id,
            qualification_id=qualification_id,
            **data.model_dump(),
        )

        return await self.repository.create(education)
