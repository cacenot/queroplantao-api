"""ProfessionalChangeDiff repository for database operations."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models.professional_change_diff import (
    ProfessionalChangeDiff,
)
from src.shared.infrastructure.repositories import BaseRepository


class ProfessionalChangeDiffRepository(BaseRepository[ProfessionalChangeDiff]):
    """
    Repository for ProfessionalChangeDiff model.

    Provides operations for managing change diffs.
    Note: Diffs are NOT soft-deleted - they are permanent records.
    """

    model = ProfessionalChangeDiff

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query(self) -> Select[tuple[ProfessionalChangeDiff]]:
        """Base query."""
        return select(ProfessionalChangeDiff)

    async def list_for_version(
        self,
        version_id: UUID,
    ) -> list[ProfessionalChangeDiff]:
        """Get all diffs for a version."""
        query = self._base_query().where(
            ProfessionalChangeDiff.version_id == version_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_many(
        self,
        diffs: list[ProfessionalChangeDiff],
    ) -> list[ProfessionalChangeDiff]:
        """Create multiple diffs at once."""
        if not diffs:
            return []
        self.session.add_all(diffs)
        return diffs
