"""Use case for soft-deleting a professional-company link."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalCompanyRepository,
)


class DeleteProfessionalCompanyUseCase:
    """Use case for soft-deleting a professional-company link."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_company_id: UUID,
        professional_id: UUID,
    ) -> None:
        """Soft delete a company link."""
        professional_company = await self.repository.get_by_id_for_professional(
            professional_company_id, professional_id
        )
        if professional_company is None:
            raise NotFoundError(
                resource="ProfessionalCompany",
                identifier=str(professional_company_id),
            )

        await self.repository.soft_delete(professional_company_id)
