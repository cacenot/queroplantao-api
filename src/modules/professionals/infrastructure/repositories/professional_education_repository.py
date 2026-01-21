"""ProfessionalEducation repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import (
    EducationLevel,
    ProfessionalEducation,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalEducationFilter,
    ProfessionalEducationSorting,
)
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeletePaginationMixin,
)


class ProfessionalEducationRepository(
    SoftDeletePaginationMixin[ProfessionalEducation],
    BaseRepository[ProfessionalEducation],
):
    """
    Repository for ProfessionalEducation model.

    Provides CRUD operations with soft delete support.
    """

    model = ProfessionalEducation

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_qualification(
        self,
        qualification_id: UUID,
    ) -> Select[tuple[ProfessionalEducation]]:
        """
        Get base query filtered by qualification.

        Args:
            qualification_id: The qualification UUID.

        Returns:
            Query filtered by qualification and excluding soft-deleted.
        """
        return self._exclude_deleted().where(
            ProfessionalEducation.qualification_id == qualification_id
        )

    async def get_by_id_for_qualification(
        self,
        id: UUID,
        qualification_id: UUID,
    ) -> ProfessionalEducation | None:
        """
        Get education by ID for a specific qualification.

        Args:
            id: The education UUID.
            qualification_id: The qualification UUID.

        Returns:
            Education if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_qualification(qualification_id).where(
                ProfessionalEducation.id == id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_qualification(
        self,
        qualification_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalEducationFilter | None = None,
        sorting: ProfessionalEducationSorting | None = None,
    ) -> PaginatedResponse[ProfessionalEducation]:
        """
        List education records for a qualification with pagination, filtering, and sorting.

        Args:
            qualification_id: The qualification UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, level, is_completed, is_verified).
            sorting: Optional sorting (id, level, end_year, created_at).

        Returns:
            Paginated list of education records.
        """
        query = self._base_query_for_qualification(qualification_id)
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

    async def list_by_level(
        self,
        qualification_id: UUID,
        level: EducationLevel,
        pagination: PaginationParams,
        *,
        filters: ProfessionalEducationFilter | None = None,
        sorting: ProfessionalEducationSorting | None = None,
    ) -> PaginatedResponse[ProfessionalEducation]:
        """
        List education records by level.

        Args:
            qualification_id: The qualification UUID.
            level: The education level.
            pagination: Pagination parameters.
            filters: Optional additional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of education records.
        """
        query = self._base_query_for_qualification(qualification_id).where(
            ProfessionalEducation.level == level
        )
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )
