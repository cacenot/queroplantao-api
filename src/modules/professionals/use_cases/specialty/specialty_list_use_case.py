"""Use case for listing all specialties."""

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import Specialty
from src.modules.professionals.infrastructure.repositories import SpecialtyRepository


class ListSpecialtiesUseCase:
    """Use case for listing all specialties."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(
        self,
        pagination: PaginationParams,
    ) -> PaginatedResponse[Specialty]:
        """
        List all active specialties.

        Args:
            pagination: Pagination parameters.

        Returns:
            Paginated list of specialties.
        """
        return await self.repository.list_all(pagination)
