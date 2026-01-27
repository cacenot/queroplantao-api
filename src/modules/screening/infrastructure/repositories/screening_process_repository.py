"""ScreeningProcess repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.screening.domain.models import (
    ScreeningProcess,
    ScreeningRequiredDocument,
    ScreeningStatus,
)
from src.modules.screening.infrastructure.filters import (
    ScreeningProcessFilter,
    ScreeningProcessSorting,
)
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeletePaginationMixin,
)


class ScreeningProcessRepository(
    SoftDeletePaginationMixin[ScreeningProcess],
    BaseRepository[ScreeningProcess],
):
    """
    Repository for ScreeningProcess model.

    Provides CRUD operations with soft delete support and multi-tenancy filtering.
    """

    model = ScreeningProcess

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_organization(
        self,
        organization_id: UUID,
    ) -> Select[tuple[ScreeningProcess]]:
        """
        Get base query filtered by organization.

        Args:
            organization_id: The organization UUID.

        Returns:
            Query filtered by organization and excluding soft-deleted.
        """
        return self._exclude_deleted().where(
            ScreeningProcess.organization_id == organization_id
        )

    async def get_by_id_for_organization(
        self,
        id: UUID,
        organization_id: UUID,
    ) -> ScreeningProcess | None:
        """
        Get screening process by ID for a specific organization.

        Args:
            id: The screening process UUID.
            organization_id: The organization UUID.

        Returns:
            ScreeningProcess if found, None otherwise.
        """
        query = self._base_query_for_organization(organization_id).where(
            ScreeningProcess.id == id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_details(
        self,
        id: UUID,
        organization_id: UUID,
    ) -> ScreeningProcess | None:
        """
        Get screening process with all related data (steps, documents, reviews).

        Args:
            id: The screening process UUID.
            organization_id: The organization UUID.

        Returns:
            ScreeningProcess with loaded relationships.
        """
        query = (
            self._base_query_for_organization(organization_id)
            .where(ScreeningProcess.id == id)
            .options(
                selectinload(ScreeningProcess.steps),
                selectinload(ScreeningProcess.required_documents).selectinload(
                    ScreeningRequiredDocument.reviews
                ),
                selectinload(ScreeningProcess.client_company),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ScreeningProcessFilter | None = None,
        sorting: ScreeningProcessSorting | None = None,
    ) -> PaginatedResponse[ScreeningProcess]:
        """
        List screening processes for an organization.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            filters: Optional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of screening processes.
        """
        base_query = self._base_query_for_organization(organization_id)
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=base_query,
        )

    async def list_for_actor(
        self,
        organization_id: UUID,
        actor_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ScreeningProcessFilter | None = None,
        sorting: ScreeningProcessSorting | None = None,
    ) -> PaginatedResponse[ScreeningProcess]:
        """
        List screening processes assigned to a specific user.

        This is the "my pending screenings" filter.

        Args:
            organization_id: The organization UUID.
            actor_id: The current actor user UUID.
            pagination: Pagination parameters.
            filters: Optional additional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of screening processes.
        """
        base_query = self._base_query_for_organization(organization_id).where(
            ScreeningProcess.current_actor_id == actor_id
        )
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=base_query,
        )

    async def get_active_by_cpf(
        self,
        organization_id: UUID,
        cpf: str,
    ) -> ScreeningProcess | None:
        """
        Get active screening for a professional by CPF.

        Active = not in terminal state (APPROVED, REJECTED, EXPIRED, CANCELLED).

        Args:
            organization_id: The organization UUID.
            cpf: The professional's CPF.

        Returns:
            Active ScreeningProcess if found, None otherwise.
        """
        terminal_statuses = [
            ScreeningStatus.APPROVED,
            ScreeningStatus.REJECTED,
            ScreeningStatus.EXPIRED,
            ScreeningStatus.CANCELLED,
        ]
        query = (
            self._base_query_for_organization(organization_id)
            .where(ScreeningProcess.professional_cpf == cpf)
            .where(ScreeningProcess.status.not_in(terminal_statuses))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_access_token(
        self,
        access_token: str,
    ) -> ScreeningProcess | None:
        """
        Get screening process by access token (for public access).

        Args:
            access_token: The secure access token.

        Returns:
            ScreeningProcess if found and not deleted, None otherwise.
        """
        query = self._exclude_deleted().where(
            ScreeningProcess.access_token == access_token
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_access_token_with_details(
        self,
        access_token: str,
    ) -> ScreeningProcess | None:
        """
        Get screening process by access token with all related data.

        Args:
            access_token: The secure access token.

        Returns:
            ScreeningProcess with loaded relationships if found, None otherwise.
        """
        query = (
            self._exclude_deleted()
            .where(ScreeningProcess.access_token == access_token)
            .options(
                selectinload(ScreeningProcess.steps),
                selectinload(ScreeningProcess.required_documents).selectinload(
                    ScreeningRequiredDocument.reviews
                ),
                selectinload(ScreeningProcess.client_company),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_status(
        self,
        organization_id: UUID,
    ) -> dict[ScreeningStatus, int]:
        """
        Count screening processes by status for an organization.

        Returns:
            Dict mapping status to count.
        """
        from sqlalchemy import func

        query = (
            select(
                ScreeningProcess.status,
                func.count(ScreeningProcess.id).label("count"),
            )
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))
            .group_by(ScreeningProcess.status)
        )
        result = await self.session.execute(query)
        rows = result.all()
        return {row.status: row.count for row in rows}
