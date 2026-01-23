"""Use case for creating a professional-company link."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import CompanyAlreadyLinkedError, ProfessionalNotFoundError
from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.domain.schemas import ProfessionalCompanyCreate
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalCompanyRepository,
)


class CreateProfessionalCompanyUseCase:
    """Use case for creating a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: ProfessionalCompanyCreate,
        created_by: UUID | None = None,
    ) -> ProfessionalCompany:
        """
        Create a new company link for a professional.

        Validates:
        - Professional exists in organization
        - Company link doesn't already exist
        """
        # Verify professional exists
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # Check link doesn't already exist
        if await self.repository.company_link_exists(professional_id, data.company_id):
            raise CompanyAlreadyLinkedError()

        professional_company = ProfessionalCompany(
            organization_professional_id=professional_id,
            created_by=created_by,
            **data.model_dump(),
        )

        return await self.repository.create(professional_company)
