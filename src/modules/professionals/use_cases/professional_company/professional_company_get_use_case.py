"""Use case for retrieving a professional-company link."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalCompanyRepository,
)


class GetProfessionalCompanyUseCase:
    """Use case for retrieving a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_company_id: UUID,
        professional_id: UUID,
    ) -> ProfessionalCompany:
        """Get a company link by ID with company data loaded."""
        professional_company = await self.repository.get_by_id_with_company(
            professional_company_id, professional_id
        )
        if professional_company is None:
            raise NotFoundError(
                resource="ProfessionalCompany",
                identifier=str(professional_company_id),
            )

        return professional_company
