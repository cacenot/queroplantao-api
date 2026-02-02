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
from src.modules.screening.domain.models.steps import ConversationStep
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
        process = await self._get_process_or_raise(
            organization_id=organization_id,
            screening_id=screening_id,
        )
        step = self._get_conversation_step_or_raise(process)
        self._validate_step_can_complete(step, completed_by)
        self._apply_step_data(step, data)
        self._handle_outcome(
            process=process,
            step=step,
            data=data,
            completed_by=completed_by,
        )

        await self._persist_step(step)

        return ConversationStepResponse.model_validate(step)

    async def _get_process_or_raise(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess:
        process = await self._load_process_with_steps(
            organization_id=organization_id,
            screening_id=screening_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        return process

    @staticmethod
    def _get_conversation_step_or_raise(
        process: ScreeningProcess,
    ) -> ConversationStep:
        step = process.conversation_step
        if not step:
            raise ScreeningStepNotFoundError(step_id="conversation")

        return step

    @staticmethod
    def _validate_step_can_complete(
        step: ConversationStep,
        completed_by: UUID,
    ) -> None:
        StepWorkflowService.validate_step_can_complete(
            step=step,
            user_id=completed_by,
            check_assignment=True,
        )

    @staticmethod
    def _apply_step_data(
        step: ConversationStep,
        data: ConversationStepCompleteRequest,
    ) -> None:
        step.notes = data.notes
        step.outcome = data.outcome

    def _handle_outcome(
        self,
        process: ScreeningProcess,
        step: ConversationStep,
        data: ConversationStepCompleteRequest,
        completed_by: UUID,
    ) -> None:
        if data.outcome == ConversationOutcome.REJECT:
            self._reject_step_and_process(
                process=process,
                step=step,
                data=data,
                completed_by=completed_by,
            )
            return

        self._approve_and_advance(
            process=process,
            step=step,
            completed_by=completed_by,
        )

    @staticmethod
    def _reject_step_and_process(
        process: ScreeningProcess,
        step: ConversationStep,
        data: ConversationStepCompleteRequest,
        completed_by: UUID,
    ) -> None:
        StepWorkflowService.complete_step(
            step=step,
            completed_by=completed_by,
            status=StepStatus.REJECTED,
            process=process,
        )
        step.rejection_reason = data.notes
        StepWorkflowService.reject_screening_process(
            process=process,
            reason=f"Rejeitado na conversa inicial: {data.notes}",
            rejected_by=completed_by,
        )

    @staticmethod
    def _approve_and_advance(
        process: ScreeningProcess,
        step: ConversationStep,
        completed_by: UUID,
    ) -> None:
        StepWorkflowService.complete_step(
            step=step,
            completed_by=completed_by,
            status=StepStatus.APPROVED,
            process=process,
        )

        if process.status != ScreeningStatus.IN_PROGRESS:
            process.status = ScreeningStatus.IN_PROGRESS

        StepWorkflowService.advance_to_next_step(
            process=process,
            current_step=step,
            next_step=process.professional_data_step,
        )

    async def _persist_step(self, step: ConversationStep) -> None:
        await self.session.flush()
        await self.session.refresh(step)

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
