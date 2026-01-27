"""Base class for step completion use cases."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningProcessNotFoundError,
    ScreeningStepAlreadyCompletedError,
    ScreeningStepNotFoundError,
    ScreeningStepNotInProgressError,
    ScreeningStepSkippedError,
)
from src.modules.screening.domain.models.enums import (
    StepStatus,
    StepType,
)
from src.modules.screening.domain.models.screening_process_step import (
    ScreeningProcessStep,
)
from src.modules.screening.domain.schemas import ScreeningProcessStepResponse
from src.modules.screening.infrastructure.repositories import (
    ScreeningProcessRepository,
    ScreeningProcessStepRepository,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models import ScreeningProcess

TRequest = TypeVar("TRequest", bound=BaseModel)


class BaseStepCompleteUseCase(ABC, Generic[TRequest]):
    """
    Abstract base class for step completion use cases.

    Provides common validation and step advancement logic.
    """

    # Subclasses must define which step type they handle
    step_type: StepType

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.step_repository = ScreeningProcessStepRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        step_id: UUID,
        data: TRequest,
        completed_by: UUID,
    ) -> ScreeningProcessStepResponse:
        """
        Complete a screening step.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.
            step_id: Step ID to complete.
            data: Step-specific data.
            completed_by: User completing the step.

        Returns:
            The completed step response.
        """
        # 1. Validate process exists
        process = await self.process_repository.get_by_id_for_organization(
            id=screening_id,
            organization_id=organization_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Validate step exists and belongs to process
        step = await self.step_repository.get_by_id(step_id)
        if not step or step.process_id != screening_id:
            raise ScreeningStepNotFoundError(step_id=str(step_id))

        # 3. Validate step status
        self._validate_step_status(step)

        # 4. Apply step-specific logic (template method)
        await self._apply_step_data(step, data, completed_by)

        # 5. Mark step as completed (unless already handled in _apply_step_data)
        if step.status == StepStatus.IN_PROGRESS:
            step.status = StepStatus.COMPLETED
            step.submitted_at = datetime.now(timezone.utc)
            step.submitted_by = completed_by

        # 6. Advance to next step or complete process
        await self._advance_to_next_step(process, step)

        await self.session.flush()
        await self.session.refresh(step)

        return ScreeningProcessStepResponse.model_validate(step)

    def _validate_step_status(self, step: ScreeningProcessStep) -> None:
        """Validate that step can be completed."""
        if step.status == StepStatus.COMPLETED:
            raise ScreeningStepAlreadyCompletedError(step_id=str(step.id))

        if step.status == StepStatus.SKIPPED:
            raise ScreeningStepSkippedError(step_id=str(step.id))

        if step.status != StepStatus.IN_PROGRESS:
            raise ScreeningStepNotInProgressError(
                step_id=str(step.id),
                current_status=step.status.value,
            )

    @abstractmethod
    async def _apply_step_data(
        self,
        step: ScreeningProcessStep,
        data: TRequest,
        completed_by: UUID,
    ) -> None:
        """
        Apply step-specific data. Must be implemented by subclasses.

        Args:
            step: The step to update.
            data: Step-specific data.
            completed_by: User completing the step.
        """
        ...

    async def _advance_to_next_step(
        self,
        process: "ScreeningProcess",
        current_step: ScreeningProcessStep,
    ) -> None:
        """Advance to next step or mark process as pending review."""
        # Skip advancement if step was rejected
        if current_step.status == StepStatus.REJECTED:
            return

        next_step = await self.step_repository.get_next_step(
            process_id=process.id,
            current_order=current_step.order,
        )

        if next_step:
            next_step.status = StepStatus.IN_PROGRESS
            next_step.started_at = datetime.now(timezone.utc)
        else:
            # All steps completed - process complete
            pass  # Status is updated by approve/reject use cases
