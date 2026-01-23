"""Use case for updating a professional-company link."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import CompanyNotFoundError
from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.domain.schemas import ProfessionalCompanyUpdate
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalCompanyRepository,
)


class UpdateProfessionalCompanyUseCase:
    """Use case for updating a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_company_id: UUID,
        professional_id: UUID,
        data: ProfessionalCompanyUpdate,
        updated_by: UUID | None = None,
    ) -> ProfessionalCompany:
        """Update an existing company link (PATCH semantics)."""
        professional_company = await self.repository.get_by_id_for_professional(
            professional_company_id, professional_id
        )
        if professional_company is None:
            raise CompanyNotFoundError()

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(professional_company, field, value)

        if updated_by:
            professional_company.updated_by = updated_by

        return await self.repository.update(professional_company)
