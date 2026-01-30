"""Use case for completing conversation step."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import (
    ScreeningProcessNotFoundError,
    ScreeningStepNotFoundError,
)
from src.modules.screening.domain.models import ScreeningProcess
from src.modules.screening.domain.models.enums import (
    ConversationOutcome,
    ScreeningStatus,
    StepStatus,
)
from src.modules.screening.domain.schemas.screening_step_complete import (
    ConversationStepCompleteRequest,
)
from src.modules.screening.domain.schemas.steps import ConversationStepResponse
from src.modules.screening.infrastructure.repositories import (
    ConversationStepRepository,
    ScreeningProcessRepository,
)
from src.modules.screening.use_cases.screening_step.helpers import StepWorkflowService


class CompleteConversationStepUseCase:
    """
    Complete the conversation step (Step 1).

    This step captures the outcome of the initial phone call with the professional.

    Outcomes:
    - PROCEED: Step is approved, advances to PROFESSIONAL_DATA step
    - REJECT: Step is rejected, entire screening process is rejected

    Validations:
    - Process must exist and belong to organization
    - Conversation step must exist for the process
    - Step must be IN_PROGRESS
    - User must be assigned to the step (if assigned_to is set)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.step_repository = ConversationStepRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        data: ConversationStepCompleteRequest,
        completed_by: UUID,
    ) -> ConversationStepResponse:
        """
        Complete the conversation step.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.
            data: Conversation step data (notes, outcome).
            completed_by: User completing the step.

        Returns:
            The completed step response.

        Raises:
            ScreeningProcessNotFoundError: If process doesn't exist.
            ScreeningStepNotFoundError: If conversation step doesn't exist.
            ScreeningStepAlreadyCompletedError: If step is already completed.
            ScreeningStepNotInProgressError: If step is not in progress.
            ScreeningStepNotAssignedToUserError: If step is not assigned to user.
        """
        # 1. Load process with all steps
        process = await self._load_process_with_steps(organization_id, screening_id)
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get conversation step
        step = process.conversation_step
        if not step:
            raise ScreeningStepNotFoundError(step_id="conversation")

        # 3. Validate step can be completed
        StepWorkflowService.validate_step_can_complete(
            step=step,
            user_id=completed_by,
            check_assignment=True,
        )

        # 4. Apply conversation data
        step.notes = data.notes
        step.outcome = data.outcome

        # 5. Handle outcome
        if data.outcome == ConversationOutcome.REJECT:
            # Reject the step and the entire process
            StepWorkflowService.complete_step(
                step=step,
                completed_by=completed_by,
                status=StepStatus.REJECTED,
            )
            step.rejection_reason = data.notes
            StepWorkflowService.reject_screening_process(
                process=process,
                reason=f"Rejeitado na conversa inicial: {data.notes}",
                rejected_by=completed_by,
            )
        else:
            # Approve the step and advance to next
            StepWorkflowService.complete_step(
                step=step,
                completed_by=completed_by,
                status=StepStatus.APPROVED,
            )

            # Start process if still in DRAFT (legacy, should not happen)
            if process.status != ScreeningStatus.IN_PROGRESS:
                process.status = ScreeningStatus.IN_PROGRESS

            # Advance to next step (professional_data_step)
            StepWorkflowService.advance_to_next_step(
                process=process,
                current_step=step,
                next_step=process.professional_data_step,
            )

        # 6. Persist changes
        await self.session.flush()
        await self.session.refresh(step)

        return ConversationStepResponse.model_validate(step)

    async def _load_process_with_steps(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess | None:
        """Load process with all step relationships."""
        from sqlmodel import select

        query = (
            select(ScreeningProcess)
            .where(ScreeningProcess.id == screening_id)
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))
            .options(
                selectinload(ScreeningProcess.conversation_step),
                selectinload(ScreeningProcess.professional_data_step),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
