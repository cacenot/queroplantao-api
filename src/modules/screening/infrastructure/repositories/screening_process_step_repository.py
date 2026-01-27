"""ScreeningProcessStep repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models import (
    ScreeningProcessStep,
    StepStatus,
    StepType,
)
from src.shared.infrastructure.repositories import BaseRepository


class ScreeningProcessStepRepository(BaseRepository[ScreeningProcessStep]):
    """
    Repository for ScreeningProcessStep model.

    Provides operations for managing steps within a screening process.
    Steps don't have soft delete - they're tied to the process lifecycle.
    """

    model = ScreeningProcessStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_process_and_type(
        self,
        process_id: UUID,
        step_type: StepType,
    ) -> ScreeningProcessStep | None:
        """
        Get a step by process ID and step type.

        Args:
            process_id: The screening process UUID.
            step_type: The step type.

        Returns:
            ScreeningProcessStep if found, None otherwise.
        """
        query = select(self.model).where(
            self.model.process_id == process_id,
            self.model.step_type == step_type,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_process(
        self,
        process_id: UUID,
    ) -> list[ScreeningProcessStep]:
        """
        List all steps for a process ordered by step order.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of steps ordered by order field.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .order_by(self.model.order)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_current_step(
        self,
        process_id: UUID,
    ) -> ScreeningProcessStep | None:
        """
        Get the current step (first non-completed required step).

        Args:
            process_id: The screening process UUID.

        Returns:
            The current step or None if all completed.
        """
        completed_statuses = [
            StepStatus.COMPLETED,
            StepStatus.APPROVED,
            StepStatus.SKIPPED,
        ]
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status.not_in(completed_statuses))
            .order_by(self.model.order)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_next_step(
        self,
        process_id: UUID,
        current_order: int,
    ) -> ScreeningProcessStep | None:
        """
        Get the next step after a given order.

        Args:
            process_id: The screening process UUID.
            current_order: The current step order.

        Returns:
            The next step or None if no more steps.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.order > current_order)
            .order_by(self.model.order)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_previous_step(
        self,
        process_id: UUID,
        current_order: int,
    ) -> ScreeningProcessStep | None:
        """
        Get the previous step before a given order.

        Args:
            process_id: The screening process UUID.
            current_order: The current step order.

        Returns:
            The previous step or None if this is the first.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.order < current_order)
            .order_by(self.model.order.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def are_all_required_completed(
        self,
        process_id: UUID,
    ) -> bool:
        """
        Check if all required steps are completed.

        Args:
            process_id: The screening process UUID.

        Returns:
            True if all required steps are completed/approved/skipped.
        """
        completed_statuses = [
            StepStatus.COMPLETED,
            StepStatus.APPROVED,
            StepStatus.SKIPPED,
        ]
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.is_required == True)  # noqa: E712
            .where(self.model.status.not_in(completed_statuses))
        )
        result = await self.session.execute(query)
        incomplete_step = result.scalar_one_or_none()
        return incomplete_step is None

    async def bulk_create(
        self,
        steps: list[ScreeningProcessStep],
    ) -> list[ScreeningProcessStep]:
        """
        Create multiple steps at once.

        Args:
            steps: List of steps to create.

        Returns:
            List of created steps.
        """
        self.session.add_all(steps)
        await self.session.flush()
        for step in steps:
            await self.session.refresh(step)
        return steps
