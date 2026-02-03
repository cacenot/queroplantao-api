"""ProfessionalVersion repository for database operations."""

from uuid import UUID

from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.professionals.domain.models.professional_version import (
    ProfessionalVersion,
)
from src.modules.professionals.infrastructure.filters.professional_version_filters import (
    ProfessionalVersionFilter,
    ProfessionalVersionSorting,
)
from src.shared.infrastructure.repositories import (
    BaseRepository,
    OrganizationScopeMixin,
    ScopePolicy,
)


class ProfessionalVersionRepository(
    OrganizationScopeMixin[ProfessionalVersion],
    BaseRepository[ProfessionalVersion],
):
    """
    Repository for ProfessionalVersion model.

    Provides CRUD operations for version history.
    Note: Versions are NOT soft-deleted - they are permanent records.
    """

    model = ProfessionalVersion
    default_scope_policy: ScopePolicy = "ORGANIZATION_ONLY"

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query(self) -> Select[tuple[ProfessionalVersion]]:
        """Base query without soft-delete filtering (versions are permanent)."""
        return select(ProfessionalVersion)

    def _base_query_for_organization(
        self,
        organization_id: UUID,
    ) -> Select[tuple[ProfessionalVersion]]:
        """Get base query filtered by organization."""
        return self._base_query().where(
            ProfessionalVersion.organization_id == organization_id
        )

    def _base_query_for_professional(
        self,
        professional_id: UUID,
        organization_id: UUID,
    ) -> Select[tuple[ProfessionalVersion]]:
        """Get base query filtered by professional and organization."""
        return self._base_query_for_organization(organization_id).where(
            ProfessionalVersion.professional_id == professional_id
        )

    async def get_by_id(
        self,
        version_id: UUID,
    ) -> ProfessionalVersion | None:
        """Get version by ID."""
        query = self._base_query().where(ProfessionalVersion.id == version_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_for_organization(
        self,
        version_id: UUID,
        organization_id: UUID,
        *,
        include_diffs: bool = False,
    ) -> ProfessionalVersion | None:
        """Get version by ID with organization validation."""
        query = self._base_query_for_organization(organization_id).where(
            ProfessionalVersion.id == version_id
        )

        if include_diffs:
            query = query.options(selectinload(ProfessionalVersion.diffs))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_current_for_professional(
        self,
        professional_id: UUID,
        organization_id: UUID,
    ) -> ProfessionalVersion | None:
        """Get the current (active) version for a professional."""
        query = self._base_query_for_professional(
            professional_id, organization_id
        ).where(ProfessionalVersion.is_current.is_(True))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_for_professional(
        self,
        professional_id: UUID,
        organization_id: UUID,
    ) -> list[ProfessionalVersion]:
        """Get all pending versions for a professional."""
        query = (
            self._base_query_for_professional(professional_id, organization_id)
            .where(ProfessionalVersion.applied_at.is_(None))
            .where(ProfessionalVersion.rejected_at.is_(None))
            .order_by(ProfessionalVersion.version_number.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_by_source(
        self,
        source_id: UUID,
        organization_id: UUID,
    ) -> ProfessionalVersion | None:
        """Get pending version by source ID (e.g., screening process)."""
        query = (
            self._base_query_for_organization(organization_id)
            .where(ProfessionalVersion.source_id == source_id)
            .where(ProfessionalVersion.applied_at.is_(None))
            .where(ProfessionalVersion.rejected_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_professional(
        self,
        professional_id: UUID,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalVersionFilter | None = None,
        sorting: ProfessionalVersionSorting | None = None,
    ) -> PaginatedResponse[ProfessionalVersion]:
        """List version history for a professional with pagination."""
        base_query = self._base_query_for_professional(professional_id, organization_id)
        return await self.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
            base_query=base_query,
        )

    async def mark_as_current(
        self,
        version: ProfessionalVersion,
    ) -> ProfessionalVersion:
        """Mark a version as current."""
        version.is_current = True
        self.session.add(version)
        return version

    async def mark_previous_as_not_current(
        self,
        professional_id: UUID,
        exclude_version_id: UUID,
    ) -> int:
        """Mark all previous versions as not current except the given one."""
        from sqlalchemy import update

        stmt = (
            update(ProfessionalVersion)
            .where(ProfessionalVersion.professional_id == professional_id)
            .where(ProfessionalVersion.is_current.is_(True))
            .where(ProfessionalVersion.id != exclude_version_id)
            .values(is_current=False)
        )
        result = await self.session.execute(stmt)
        return result.rowcount
