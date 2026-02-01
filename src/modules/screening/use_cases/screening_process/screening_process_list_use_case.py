"""
List screening processes use case.

Lists screening processes with pagination and filters.
"""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models import ScreeningProcess
from src.modules.screening.infrastructure.filters import (
    ScreeningProcessFilter,
    ScreeningProcessSorting,
)
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository


class ListScreeningProcessesUseCase:
    """List screening processes for an organization."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
        filters: ScreeningProcessFilter | None = None,
        sorting: ScreeningProcessSorting | None = None,
    ) -> PaginatedResponse[ScreeningProcess]:
        """
        List screening processes with pagination.

        Args:
            organization_id: The organization ID.
            pagination: Pagination parameters.
            family_org_ids: Organization family IDs for scope validation.
            filters: Optional filter parameters.
            sorting: Optional sorting parameters.

        Returns:
            Paginated list of screening processes.
        """
        return await self.repository.list_for_organization(
            organization_id=organization_id,
            pagination=pagination,
            family_org_ids=family_org_ids,
            filters=filters,
            sorting=sorting,
        )
