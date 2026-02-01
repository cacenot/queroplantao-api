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
    StepStatus,
    StepType,
)
from src.modules.screening.domain.schemas import ScreeningProcessStepResponse
from src.modules.screening.infrastructure.repositories import (
    ScreeningProcessRepository,
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

    async def execute(
        self,
        organization_id: UUID,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
        screening_id: UUID,
        target_step_id: UUID,
        requested_by: UUID,
    ) -> ScreeningProcessStepResponse:
        """
        Go back to a specific step.

        Args:
            organization_id: Organization ID.
            family_org_ids: Organization family IDs for scope validation.
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
        process = await self.process_repository.get_by_id_with_details(
            id=screening_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get all steps from process
        all_steps = [
            process.conversation_step,
            process.professional_data_step,
            process.document_upload_step,
            process.document_review_step,
            process.payment_info_step,
            process.client_validation_step,
        ]
        all_steps = [step for step in all_steps if step is not None]

        # 3. Find target step
        target_step = next(
            (step for step in all_steps if step.id == target_step_id),
            None,
        )
        if not target_step:
            raise ScreeningStepNotFoundError(step_id=str(target_step_id))

        # 4. Validate can go back to this step
        if target_step.step_type in NON_REVERSIBLE_STEPS:
            raise ScreeningStepCannotGoBackError(step_type=target_step.step_type.value)

        # 5. Get all steps ordered
        all_steps_sorted = sorted(all_steps, key=lambda s: s.order)

        # 6. Reset steps after target
        for step in all_steps_sorted:
            if step.order > target_step.order:
                if step.status != StepStatus.SKIPPED:
                    step.status = StepStatus.PENDING
                    step.started_at = None
                    step.submitted_at = None
                    step.submitted_by = None

        # 7. Set target step as in progress
        target_step.status = StepStatus.IN_PROGRESS
        target_step.started_at = datetime.now(timezone.utc)

        # 8. Process status stays as IN_PROGRESS
        # (status is already IN_PROGRESS for active screenings)

        await self.session.flush()
        await self.session.refresh(target_step)

        return ScreeningProcessStepResponse.model_validate(target_step)
