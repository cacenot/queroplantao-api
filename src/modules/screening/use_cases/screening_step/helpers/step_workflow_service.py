"""Step workflow service with common step operations."""

from datetime import datetime, timezone
from typing import Union
from uuid import UUID

from src.app.exceptions import (
    ScreeningStepAlreadyCompletedError,
    ScreeningStepNotAssignedToUserError,
    ScreeningStepNotInProgressError,
    ScreeningStepSkippedError,
)
from src.modules.screening.domain.models import ScreeningProcess, ScreeningStatus
from src.modules.screening.domain.models.enums import StepStatus, StepType
from src.modules.screening.domain.models.steps import (
    ClientValidationStep,
    ConversationStep,
    DocumentReviewStep,
    DocumentUploadStep,
    PaymentInfoStep,
    ProfessionalDataStep,
    ScreeningStepMixin,
)

# Type alias for any step model
AnyStep = Union[
    ConversationStep,
    ProfessionalDataStep,
    DocumentUploadStep,
    DocumentReviewStep,
    PaymentInfoStep,
    ClientValidationStep,
]


class StepWorkflowService:
    """
    Service with common step workflow operations.

    Provides reusable functions for:
    - Validating step status before completion
    - Validating step assignment
    - Advancing to next step
    - Rejecting the screening process
    """

    @staticmethod
    def validate_step_can_complete(
        step: ScreeningStepMixin,
        user_id: UUID,
        *,
        check_assignment: bool = True,
    ) -> None:
        """
        Validate that a step can be completed.

        Checks:
        1. Step is not already completed/approved
        2. Step is not skipped
        3. Step is in progress
        4. Step is assigned to the user (optional)

        Args:
            step: The step to validate.
            user_id: The user trying to complete the step.
            check_assignment: Whether to validate assigned_to. Defaults to True.

        Raises:
            ScreeningStepAlreadyCompletedError: If step is already completed.
            ScreeningStepSkippedError: If step was skipped.
            ScreeningStepNotInProgressError: If step is not in progress.
            ScreeningStepNotAssignedToUserError: If step is not assigned to user.
        """
        step_id_str = str(step.id)

        if step.status in (StepStatus.COMPLETED, StepStatus.APPROVED):
            raise ScreeningStepAlreadyCompletedError(step_id=step_id_str)

        if step.status == StepStatus.SKIPPED:
            raise ScreeningStepSkippedError(step_id=step_id_str)

        if step.status != StepStatus.IN_PROGRESS:
            raise ScreeningStepNotInProgressError(
                step_id=step_id_str,
                current_status=step.status.value,
            )

        if (
            check_assignment
            and step.assigned_to is not None
            and step.assigned_to != user_id
        ):
            raise ScreeningStepNotAssignedToUserError(
                step_id=step_id_str, user_id=str(user_id)
            )

    @staticmethod
    def advance_to_next_step(
        process: ScreeningProcess,
        current_step: ScreeningStepMixin,
        next_step: AnyStep | None = None,
    ) -> StepType | None:
        """
        Advance to the next step in the workflow.

        Updates process.current_step_type to the next step type.
        If next_step is provided, also starts it (sets status and started_at).

        Args:
            process: The screening process.
            current_step: The step that was just completed.
            next_step: The next step model (if already loaded). If provided,
                      will be started (status=IN_PROGRESS, started_at=now).

        Returns:
            The next step type if found, None if this was the last step.
        """
        configured_steps = process.configured_step_types
        current_step_type = current_step.step_type.value

        # Find current step index in configured steps
        try:
            current_index = configured_steps.index(current_step_type)
        except ValueError:
            return None

        # Check if there's a next step
        next_index = current_index + 1
        if next_index >= len(configured_steps):
            # This was the last step, keep current_step_type at last value
            return None

        # Get next step type
        next_step_type_value = configured_steps[next_index]
        next_step_type = StepType(next_step_type_value)

        # Update process current_step_type
        process.current_step_type = next_step_type

        # If next step model is provided, start it
        if next_step is not None:
            next_step.status = StepStatus.IN_PROGRESS
            next_step.started_at = datetime.now(timezone.utc)

        return next_step_type

    @staticmethod
    def reject_screening_process(
        process: ScreeningProcess,
        reason: str,
        rejected_by: UUID,
    ) -> None:
        """
        Reject the entire screening process.

        Sets status to REJECTED and records the rejection details.

        Args:
            process: The screening process to reject.
            reason: The reason for rejection.
            rejected_by: The user who rejected.
        """
        process.status = ScreeningStatus.REJECTED
        process.rejection_reason = reason
        process.completed_at = datetime.now(timezone.utc)
        process.updated_by = rejected_by

    @staticmethod
    def complete_step(
        step: ScreeningStepMixin,
        completed_by: UUID,
        *,
        status: StepStatus = StepStatus.APPROVED,
    ) -> None:
        """
        Mark a step as completed.

        Args:
            step: The step to complete.
            completed_by: The user completing the step.
            status: The final status. Defaults to APPROVED.
        """
        step.status = status
        step.completed_at = datetime.now(timezone.utc)
        step.completed_by = completed_by
