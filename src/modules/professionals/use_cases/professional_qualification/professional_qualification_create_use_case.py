"""Use case for creating a professional qualification."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    CouncilRegistrationExistsError,
    InvalidCouncilTypeError,
    ProfessionalNotFoundError,
)
from src.modules.professionals.domain.models import (
    ProfessionalQualification,
    validate_council_for_professional_type,
)
from src.modules.professionals.domain.schemas import ProfessionalQualificationCreate
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalQualificationRepository,
)


class CreateProfessionalQualificationUseCase:
    """Use case for creating a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: ProfessionalQualificationCreate,
    ) -> ProfessionalQualification:
        """
        Create a new qualification for a professional.

        Validates:
        - Professional exists in organization
        - Council type matches professional type
        - Council registration is unique in organization
        """
        # Verify professional exists
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # Validate council matches professional type
        if not validate_council_for_professional_type(
            data.council_type, data.professional_type
        ):
            raise InvalidCouncilTypeError(
                details={
                    "council_type": data.council_type.value,
                    "professional_type": data.professional_type.value,
                }
            )

        # Validate council uniqueness in organization
        if await self.repository.council_exists_in_organization(
            data.council_number, data.council_state, organization_id
        ):
            raise CouncilRegistrationExistsError()

        qualification = ProfessionalQualification(
            organization_id=organization_id,
            organization_professional_id=professional_id,
            **data.model_dump(),
        )

        return await self.repository.create(qualification)
