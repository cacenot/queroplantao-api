"""Use case for completing client validation step."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningClientValidationNotRequiredError,
    ScreeningStepInvalidTypeError,
)
from src.modules.screening.domain.models.enums import (
    ClientValidationOutcome,
    ScreeningStatus,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.models.screening_process_step import (
    ScreeningProcessStep,
)
from src.modules.screening.domain.schemas.screening_step_complete import (
    ClientValidationStepCompleteRequest,
)
from src.modules.screening.use_cases.screening_step.base_step_complete_use_case import (
    BaseStepCompleteUseCase,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models import ScreeningProcess


class CompleteClientValidationStepUseCase(
    BaseStepCompleteUseCase[ClientValidationStepCompleteRequest]
):
    """
    Complete the client validation step (Step 10 - Optional).

    This step is only present when client_validation_required=True on the process.
    Captures the client's decision to approve or reject the professional.
    """

    step_type = StepType.CLIENT_VALIDATION

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def _apply_step_data(
        self,
        step: ScreeningProcessStep,
        data: ClientValidationStepCompleteRequest,
        completed_by: UUID,
    ) -> None:
        """Apply client validation data."""
        # Validate step type
        if step.step_type != StepType.CLIENT_VALIDATION:
            raise ScreeningStepInvalidTypeError(
                expected=StepType.CLIENT_VALIDATION.value,
                received=step.step_type.value,
            )

        # Validate client validation is required
        process = await self.process_repository.get_by_id(step.process_id)
        if process and not process.client_validation_required:
            raise ScreeningClientValidationNotRequiredError()

        # Save client validation data
        step.client_validation_outcome = data.outcome
        step.client_validation_notes = data.notes
        step.client_validated_by = data.validated_by_name
        step.client_validated_at = datetime.now(timezone.utc)

        # If client rejected, update process status
        if data.outcome == ClientValidationOutcome.REJECTED:
            if process:
                process.status = ScreeningStatus.REJECTED
                process.completed_at = datetime.now(timezone.utc)
                process.notes = f"Rejeitado pelo cliente ({data.validated_by_name}): {data.notes or 'Sem motivo'}"

            step.status = StepStatus.REJECTED
            step.rejection_reason = data.notes
            step.submitted_at = datetime.now(timezone.utc)
            step.submitted_by = completed_by

    async def _advance_to_next_step(
        self,
        process: "ScreeningProcess",
        current_step: ScreeningProcessStep,
    ) -> None:
        """Only advance if client approved."""
        if current_step.client_validation_outcome == ClientValidationOutcome.APPROVED:
            await super()._advance_to_next_step(process, current_step)
