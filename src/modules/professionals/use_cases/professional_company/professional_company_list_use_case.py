"""Use case for listing company links for a professional."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalCompanyRepository,
)


class ListProfessionalCompaniesUseCase:
    """Use case for listing company links for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        active_only: bool = False,
    ) -> PaginatedResponse[ProfessionalCompany]:
        """List company links for a professional."""
        if active_only:
            return await self.repository.list_active_companies(
                professional_id, pagination
            )
        return await self.repository.list_for_professional(professional_id, pagination)
