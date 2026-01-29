"""ScreeningAlert repository for database operations."""

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models.screening_alert import ScreeningAlert
from src.shared.infrastructure.repositories import BaseRepository


class ScreeningAlertRepository(BaseRepository[ScreeningAlert]):
    """
    Repository for ScreeningAlert model.

    Provides CRUD operations for screening alerts.
    Alerts don't use soft delete - they're tied to the process lifecycle.
    """

    model = ScreeningAlert

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query(self) -> Select[tuple[ScreeningAlert]]:
        """Get base query for alerts."""
        return select(ScreeningAlert)

    def _base_query_for_process(
        self,
        process_id: UUID,
    ) -> Select[tuple[ScreeningAlert]]:
        """
        Get base query filtered by process.

        Args:
            process_id: The screening process UUID.

        Returns:
            Query filtered by process.
        """
        return self._base_query().where(ScreeningAlert.process_id == process_id)

    async def get_by_id_for_process(
        self,
        alert_id: UUID,
        process_id: UUID,
    ) -> ScreeningAlert | None:
        """
        Get alert by ID for a specific process.

        Args:
            alert_id: The alert UUID.
            process_id: The screening process UUID.

        Returns:
            ScreeningAlert if found, None otherwise.
        """
        query = self._base_query_for_process(process_id).where(
            ScreeningAlert.id == alert_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_for_process(
        self,
        process_id: UUID,
    ) -> ScreeningAlert | None:
        """
        Get the pending (unresolved) alert for a process, if any.

        There should be at most one pending alert per process.

        Args:
            process_id: The screening process UUID.

        Returns:
            The pending alert if exists, None otherwise.
        """
        query = (
            self._base_query_for_process(process_id)
            .where(ScreeningAlert.is_resolved.is_(False))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def has_pending_alert(
        self,
        process_id: UUID,
    ) -> bool:
        """
        Check if there's a pending alert for a process.

        Args:
            process_id: The screening process UUID.

        Returns:
            True if there's a pending alert, False otherwise.
        """
        query = (
            select(ScreeningAlert.id)
            .where(ScreeningAlert.process_id == process_id)
            .where(ScreeningAlert.is_resolved.is_(False))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def list_for_process(
        self,
        process_id: UUID,
    ) -> list[ScreeningAlert]:
        """
        List all alerts for a process, ordered by created_at descending.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of alerts for the process.
        """
        query = self._base_query_for_process(process_id).order_by(
            ScreeningAlert.created_at.desc()
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_for_process(
        self,
        process_id: UUID,
    ) -> tuple[int, int]:
        """
        Count alerts for a process (total and pending).

        Args:
            process_id: The screening process UUID.

        Returns:
            Tuple of (total_count, pending_count).
        """
        query = select(
            func.count(ScreeningAlert.id).label("total"),
            func.count(ScreeningAlert.id)
            .filter(ScreeningAlert.is_resolved.is_(False))
            .label("pending"),
        ).where(ScreeningAlert.process_id == process_id)

        result = await self.session.execute(query)
        row = result.one()
        return (row.total, row.pending)
