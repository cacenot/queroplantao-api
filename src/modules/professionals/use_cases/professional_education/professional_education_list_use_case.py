"""Use case for listing education records for a qualification."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import (
    EducationLevel,
    ProfessionalEducation,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalEducationRepository,
)


class ListProfessionalEducationsUseCase:
    """Use case for listing education records for a qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        pagination: PaginationParams,
        *,
        level: EducationLevel | None = None,
        is_completed: bool | None = None,
    ) -> PaginatedResponse[ProfessionalEducation]:
        """List education records for a qualification."""
        return await self.repository.list_for_qualification(
            qualification_id,
            pagination,
            level=level,
            is_completed=is_completed,
        )
