"""Use case for searching specialties by name."""

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models.specialty import Specialty
from src.shared.infrastructure.filters.specialty import SpecialtySorting
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)


class SearchSpecialtiesUseCase:
    """Use case for searching specialties by name."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(
        self,
        name: str,
        pagination: PaginationParams,
        *,
        sorting: SpecialtySorting | None = None,
    ) -> PaginatedResponse[Specialty]:
        """
        Search specialties by name (case-insensitive partial match).

        Args:
            name: The search term.
            pagination: Pagination parameters.
            sorting: Optional sorting.

        Returns:
            Paginated list of matching specialties.
        """
        return await self.repository.search_by_name(name, pagination, sorting=sorting)
