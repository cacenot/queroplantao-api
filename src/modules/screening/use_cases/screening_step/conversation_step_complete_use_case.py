"""Use case for completing conversation step."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ScreeningStepInvalidTypeError
from src.modules.screening.domain.models.enums import (
    ConversationOutcome,
    ScreeningStatus,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.models.screening_process_step import (
    ScreeningProcessStep,
)
from src.modules.screening.domain.schemas.screening_step_complete import (
    ConversationStepCompleteRequest,
)
from src.modules.screening.use_cases.screening_step.base_step_complete_use_case import (
    BaseStepCompleteUseCase,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models import ScreeningProcess


class CompleteConversationStepUseCase(
    BaseStepCompleteUseCase[ConversationStepCompleteRequest]
):
    """
    Complete the conversation step (Step 1).

    This step captures the outcome of the initial phone call with the professional.
    If outcome is REJECT, the entire screening process is cancelled.
    """

    step_type = StepType.CONVERSATION

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def _apply_step_data(
        self,
        step: ScreeningProcessStep,
        data: ConversationStepCompleteRequest,
        completed_by: UUID,
    ) -> None:
        """Apply conversation-specific data to the step."""
        # Validate step type
        if step.step_type != StepType.CONVERSATION:
            raise ScreeningStepInvalidTypeError(
                expected=StepType.CONVERSATION.value,
                received=step.step_type.value,
            )

        # Save conversation data
        step.conversation_notes = data.notes
        step.conversation_outcome = data.outcome

        # If rejected, cancel the process
        if data.outcome == ConversationOutcome.REJECT:
            process = await self.process_repository.get_by_id(step.process_id)
            if process:
                process.status = ScreeningStatus.CANCELLED
                process.completed_at = datetime.now(timezone.utc)
                process.notes = f"Rejeitado na conversa inicial: {data.notes}"

                # Mark step as rejected instead of completed
                step.status = StepStatus.REJECTED
                step.rejection_reason = data.notes
                step.submitted_at = datetime.now(timezone.utc)
                step.submitted_by = completed_by

    async def _advance_to_next_step(
        self,
        process: "ScreeningProcess",
        current_step: ScreeningProcessStep,
    ) -> None:
        """Only advance if conversation outcome was PROCEED."""
        if current_step.conversation_outcome == ConversationOutcome.PROCEED:
            await super()._advance_to_next_step(process, current_step)
        # If REJECT, process was already cancelled in _apply_step_data
