"""Use case for going back to a previous step."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningProcessNotFoundError,
    ScreeningStepCannotGoBackError,
    ScreeningStepNotFoundError,
)
from src.modules.screening.domain.models.enums import (
    ScreeningStatus,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.schemas import ScreeningProcessStepResponse
from src.modules.screening.infrastructure.repositories import (
    ScreeningProcessRepository,
    ScreeningProcessStepRepository,
)

# Steps that cannot be revisited
NON_REVERSIBLE_STEPS = {
    StepType.CONVERSATION,  # Conversa inicial não pode ser refeita
}


class GoBackToStepUseCase:
    """
    Go back to a previous step in the screening process.

    Resets all steps after the target step to PENDING status.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.step_repository = ScreeningProcessStepRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        target_step_id: UUID,
        requested_by: UUID,
    ) -> ScreeningProcessStepResponse:
        """
        Go back to a specific step.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.
            target_step_id: Step ID to go back to.
            requested_by: User requesting the action.

        Returns:
            The target step response (now in progress).

        Raises:
            ScreeningProcessNotFoundError: If process not found.
            ScreeningStepNotFoundError: If step not found.
            ScreeningStepCannotGoBackError: If cannot go back to this step.
        """
        # 1. Validate process
        process = await self.process_repository.get_by_id_for_organization(
            id=screening_id,
            organization_id=organization_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get target step
        target_step = await self.step_repository.get_by_id(target_step_id)
        if not target_step or target_step.process_id != screening_id:
            raise ScreeningStepNotFoundError(step_id=str(target_step_id))

        # 3. Validate can go back to this step
        if target_step.step_type in NON_REVERSIBLE_STEPS:
            raise ScreeningStepCannotGoBackError(step_type=target_step.step_type.value)

        # 4. Get all steps ordered
        all_steps = await self.step_repository.list_by_process(screening_id)
        all_steps_sorted = sorted(all_steps, key=lambda s: s.order)

        # 5. Reset steps after target
        for step in all_steps_sorted:
            if step.order > target_step.order:
                if step.status != StepStatus.SKIPPED:
                    step.status = StepStatus.PENDING
                    step.started_at = None
                    step.submitted_at = None
                    step.submitted_by = None

        # 6. Set target step as in progress
        target_step.status = StepStatus.IN_PROGRESS
        target_step.started_at = datetime.now(timezone.utc)

        # 7. Update process status if needed
        if process.status == ScreeningStatus.PENDING_REVIEW:
            process.status = ScreeningStatus.IN_PROGRESS

        await self.session.flush()
        await self.session.refresh(target_step)

        return ScreeningProcessStepResponse.model_validate(target_step)
