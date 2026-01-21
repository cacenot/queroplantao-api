"""Use case for listing qualifications for a professional."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import ProfessionalQualification
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
)


class ListProfessionalQualificationsUseCase:
    """Use case for listing qualifications for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ProfessionalQualification]:
        """List qualifications for a professional."""
        return await self.repository.list_for_professional(professional_id, pagination)
