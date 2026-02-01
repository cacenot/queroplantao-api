"""Use case for creating a professional specialty."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    GlobalSpecialtyNotFoundError,
    QualificationNotFoundError,
    SpecialtyAlreadyAssignedError,
)
from src.modules.professionals.domain.models import ProfessionalSpecialty
from src.modules.professionals.domain.schemas import ProfessionalSpecialtyCreate
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
    SpecialtyRepository,
)


class CreateProfessionalSpecialtyUseCase:
    """Use case for creating a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)
        self.specialty_repository = SpecialtyRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        data: ProfessionalSpecialtyCreate,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
    ) -> ProfessionalSpecialty:
        """
        Create a new specialty for a qualification.

        Validates:
        - Qualification exists in organization
        - Specialty exists
        - Specialty is not already assigned to this qualification
        """
        # Verify qualification exists
        qualification = await self.qualification_repository.get_by_organization(
            id=qualification_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
        )
        if qualification is None:
            raise QualificationNotFoundError()

        # Verify specialty exists
        specialty = await self.specialty_repository.get_by_id(data.specialty_id)
        if specialty is None:
            raise GlobalSpecialtyNotFoundError(specialty_id=str(data.specialty_id))

        # Check specialty not already assigned
        if await self.repository.specialty_exists_for_qualification(
            qualification_id, data.specialty_id
        ):
            raise SpecialtyAlreadyAssignedError()

        professional_specialty = ProfessionalSpecialty(
            qualification_id=qualification_id,
            **data.model_dump(),
        )

        return await self.repository.create(professional_specialty)
