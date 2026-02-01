"""Use case for listing all specialties."""

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models.specialty import Specialty
from src.shared.infrastructure.filters.specialty import (
    SpecialtyFilter,
    SpecialtySorting,
)
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)


class ListSpecialtiesUseCase:
    """Use case for listing all specialties."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(
        self,
        pagination: PaginationParams,
        *,
        filters: SpecialtyFilter | None = None,
        sorting: SpecialtySorting | None = None,
    ) -> PaginatedResponse[Specialty]:
        """
        List all active specialties.

        Args:
            pagination: Pagination parameters.
            filters: Optional filters (search by code, name).
            sorting: Optional sorting (id, code, name). Defaults to name asc.

        Returns:
            Paginated list of specialties.
        """
        return await self.repository.list_all(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
        )
