"""Cancel screening process use case."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningProcessCannotCancelError,
    ScreeningProcessNotFoundError,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)
from src.modules.screening.domain.models.enums import ScreeningStatus, StepStatus
from src.modules.screening.domain.models.screening_process import ScreeningProcess
from src.modules.screening.domain.schemas import ScreeningProcessResponse
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository


class CancelScreeningProcessUseCase:
    """
    Cancel a screening process.

    Marks the screening as CANCELLED with a reason, cancels all active steps,
    and soft-deletes any orphan pending documents.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.document_repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        cancelled_by: UUID,
        reason: str,
    ) -> ScreeningProcessResponse:
        """
        Cancel the screening process.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            cancelled_by: The user cancelling the screening.
            reason: The cancellation reason (required).

        Returns:
            The cancelled screening process response.

        Raises:
            ScreeningProcessNotFoundError: If screening not found.
            ScreeningProcessCannotCancelError: If screening cannot be cancelled.
        """
        process = await self.repository.get_by_id_with_details(
            id=screening_id,
            organization_id=organization_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # Validate screening can be cancelled
        if process.status in (
            ScreeningStatus.APPROVED,
            ScreeningStatus.REJECTED,
            ScreeningStatus.CANCELLED,
        ):
            raise ScreeningProcessCannotCancelError(current_status=process.status.value)

        # Cancel the screening
        process.status = ScreeningStatus.CANCELLED
        process.cancelled_at = datetime.now(UTC)
        process.cancelled_by = cancelled_by
        process.cancellation_reason = reason
        process.updated_by = cancelled_by

        # Cancel all active steps
        self._cancel_active_steps(process)

        # Soft-delete orphan pending documents
        await self.document_repository.soft_delete_orphan_pending_documents(
            screening_id=screening_id,
            deleted_by=cancelled_by,
        )

        await self.session.flush()
        await self.session.refresh(process)

        return ScreeningProcessResponse.model_validate(process)

    def _cancel_active_steps(self, process: ScreeningProcess) -> None:
        """Cancel all steps that are pending or in progress."""
        active_statuses = (StepStatus.PENDING, StepStatus.IN_PROGRESS)

        all_steps = [
            process.conversation_step,
            process.professional_data_step,
            process.document_upload_step,
            process.document_review_step,
            process.payment_info_step,
            process.client_validation_step,
        ]

        for step in all_steps:
            if step is not None and step.status in active_statuses:
                step.status = StepStatus.CANCELLED
