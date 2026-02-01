"""Specialty repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models.specialty import Specialty
from src.shared.infrastructure.filters.specialty import (
    SpecialtyFilter,
    SpecialtySorting,
)
from src.shared.infrastructure.repositories.base import BaseRepository
from src.shared.infrastructure.repositories.mixins import SoftDeleteMixin


class SpecialtyRepository(
    SoftDeleteMixin[Specialty],
    BaseRepository[Specialty],
):
    """
    Repository for Specialty model.

    Provides read operations for the global specialty reference table.
    Specialties are managed by administrators, not by organization users.
    """

    model = Specialty

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_code(self, code: str) -> Specialty | None:
        """
        Get specialty by code.

        Args:
            code: The specialty code (e.g., 'CARDIOLOGIA').

        Returns:
            Specialty if found, None otherwise.
        """
        result = await self.session.execute(
            self.get_query().where(Specialty.code == code)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        pagination: PaginationParams,
        *,
        filters: SpecialtyFilter | None = None,
        sorting: SpecialtySorting | None = None,
    ) -> PaginatedResponse[Specialty]:
        """
        List all active specialties with pagination, filtering, and sorting.

        Args:
            pagination: Pagination parameters.
            filters: Optional filters (search by code, name).
            sorting: Optional sorting (id, code, name). Defaults to name asc.

        Returns:
            Paginated list of specialties.
        """
        return await self.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
        )

    async def search_by_name(
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
        query = self.get_query().where(Specialty.name.ilike(f"%{name}%"))
        return await self.list(
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
            base_query=query,
        )

    async def get_by_ids(self, ids: list[UUID]) -> list[Specialty]:
        """
        Get multiple specialties by their IDs.

        Args:
            ids: List of specialty UUIDs.

        Returns:
            List of specialties found.
        """
        if not ids:
            return []

        result = await self.session.execute(
            self.get_query().where(Specialty.id.in_(ids))
        )
        return list(result.scalars().all())

    async def code_exists(
        self,
        code: str,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a specialty code already exists.

        Args:
            code: The specialty code.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if code exists, False otherwise.
        """
        query = self.get_query().where(Specialty.code == code)
        if exclude_id:
            query = query.where(Specialty.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()
