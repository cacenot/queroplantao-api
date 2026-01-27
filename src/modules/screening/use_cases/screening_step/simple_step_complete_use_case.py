"""Use case for completing simple steps (no specific data required)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ScreeningStepInvalidTypeError
from src.modules.screening.domain.models.enums import StepType
from src.modules.screening.domain.models.screening_process_step import (
    ScreeningProcessStep,
)
from src.modules.screening.domain.schemas.screening_step_complete import (
    SimpleStepCompleteRequest,
)
from src.modules.screening.use_cases.screening_step.base_step_complete_use_case import (
    BaseStepCompleteUseCase,
)


# Steps that use the simple completion flow
SIMPLE_STEP_TYPES = {
    StepType.PROFESSIONAL_DATA,
    StepType.QUALIFICATION,
    StepType.SPECIALTY,
    StepType.EDUCATION,
    StepType.COMPANY,
    StepType.BANK_ACCOUNT,
}


class CompleteSimpleStepUseCase(BaseStepCompleteUseCase[SimpleStepCompleteRequest]):
    """
    Complete a simple step that doesn't require specific data.

    Used for: PROFESSIONAL_DATA, QUALIFICATION, SPECIALTY,
    EDUCATION, COMPANY, BANK_ACCOUNT.

    These steps only require marking as completed. The actual data
    is saved in separate entities (Professional, Qualification, etc.)
    and linked via data_references.
    """

    step_type = StepType.PROFESSIONAL_DATA  # Default, validated dynamically

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def _apply_step_data(
        self,
        step: ScreeningProcessStep,
        data: SimpleStepCompleteRequest,
        completed_by: UUID,
    ) -> None:
        """Apply simple step data (only notes)."""
        # Validate step type is one of the simple types
        if step.step_type not in SIMPLE_STEP_TYPES:
            raise ScreeningStepInvalidTypeError(
                expected=", ".join(t.value for t in SIMPLE_STEP_TYPES),
                received=step.step_type.value,
            )

        # Only save notes if provided
        if data.notes:
            step.review_notes = data.notes
