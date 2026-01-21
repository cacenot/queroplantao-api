"""Use case for searching specialties by name."""

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import Specialty
from src.modules.professionals.infrastructure.repositories import SpecialtyRepository


class SearchSpecialtiesUseCase:
    """Use case for searching specialties by name."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(
        self,
        name: str,
        pagination: PaginationParams,
    ) -> PaginatedResponse[Specialty]:
        """
        Search specialties by name (case-insensitive partial match).

        Args:
            name: The search term.
            pagination: Pagination parameters.

        Returns:
            Paginated list of matching specialties.
        """
        return await self.repository.search_by_name(name, pagination)
