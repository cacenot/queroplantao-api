"""Use case for listing specialties for a qualification."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import ProfessionalSpecialty
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalSpecialtyRepository,
)


class ListProfessionalSpecialtiesUseCase:
    """Use case for listing specialties for a qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ProfessionalSpecialty]:
        """List specialties for a qualification."""
        return await self.repository.list_for_qualification(
            qualification_id, pagination
        )
