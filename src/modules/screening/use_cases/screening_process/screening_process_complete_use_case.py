"""
Complete screening process use case.

Handles final approval or rejection of the screening.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningProcessCannotApproveError,
    ScreeningProcessCannotCancelError,
    ScreeningProcessCannotRejectError,
    ScreeningProcessHasRejectedDocumentsError,
    ScreeningProcessIncompleteStepsError,
    ScreeningProcessNotFoundError,
)
from src.modules.screening.domain.models.enums import ScreeningStatus
from src.modules.screening.domain.schemas import ScreeningProcessResponse
from src.modules.screening.infrastructure.repositories import (
    ScreeningDocumentReviewRepository,
    ScreeningProcessRepository,
    ScreeningProcessStepRepository,
)


class ApproveScreeningProcessUseCase:
    """
    Approve a screening process.

    Marks the screening as APPROVED and the professional as verified.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.step_repository = ScreeningProcessStepRepository(session)
        self.review_repository = ScreeningDocumentReviewRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        approved_by: UUID,
        notes: str | None = None,
    ) -> ScreeningProcessResponse:
        """
        Approve the screening process.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            approved_by: The user approving the screening.
            notes: Optional approval notes.

        Returns:
            The approved screening process response.

        Raises:
            NotFoundError: If screening not found.
            ValidationError: If screening cannot be approved.
        """
        process = await self.repository.get_by_id_for_organization(
            organization_id=organization_id,
            entity_id=screening_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # Validate screening status
        if process.status != ScreeningStatus.IN_PROGRESS:
            raise ScreeningProcessCannotApproveError(
                current_status=process.status.value
            )

        # Check if all required steps are completed
        all_completed = await self.step_repository.are_all_required_completed(
            screening_id
        )
        if not all_completed:
            raise ScreeningProcessIncompleteStepsError()

        # Check if there are any document rejections
        has_rejections = await self.review_repository.has_rejections(screening_id)
        if has_rejections:
            raise ScreeningProcessHasRejectedDocumentsError()

        # Approve the screening
        process.status = ScreeningStatus.APPROVED
        process.completed_at = datetime.now(timezone.utc)
        process.updated_by = approved_by
        if notes:
            process.notes = notes

        await self.session.flush()
        await self.session.refresh(process)

        # TODO: Mark professional as verified
        # TODO: Send notification to professional

        return ScreeningProcessResponse.model_validate(process)


class RejectScreeningProcessUseCase:
    """
    Reject a screening process.

    Marks the screening as REJECTED with a reason.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        rejected_by: UUID,
        reason: str,
    ) -> ScreeningProcessResponse:
        """
        Reject the screening process.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            rejected_by: The user rejecting the screening.
            reason: The rejection reason.

        Returns:
            The rejected screening process response.

        Raises:
            NotFoundError: If screening not found.
            ValidationError: If screening cannot be rejected.
        """
        process = await self.repository.get_by_id_for_organization(
            organization_id=organization_id,
            entity_id=screening_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # Validate screening status
        if process.status in [ScreeningStatus.APPROVED, ScreeningStatus.CANCELLED]:
            raise ScreeningProcessCannotRejectError(current_status=process.status.value)

        # Reject the screening
        process.status = ScreeningStatus.REJECTED
        process.completed_at = datetime.now(timezone.utc)
        process.notes = reason
        process.updated_by = rejected_by

        await self.session.flush()
        await self.session.refresh(process)

        # TODO: Send notification to professional

        return ScreeningProcessResponse.model_validate(process)


class CancelScreeningProcessUseCase:
    """
    Cancel a screening process.

    Marks the screening as CANCELLED.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        cancelled_by: UUID,
        reason: str | None = None,
    ) -> ScreeningProcessResponse:
        """
        Cancel the screening process.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            cancelled_by: The user cancelling the screening.
            reason: Optional cancellation reason.

        Returns:
            The cancelled screening process response.

        Raises:
            NotFoundError: If screening not found.
            ValidationError: If screening cannot be cancelled.
        """
        process = await self.repository.get_by_id_for_organization(
            organization_id=organization_id,
            entity_id=screening_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # Validate screening status
        if process.status in [
            ScreeningStatus.APPROVED,
            ScreeningStatus.REJECTED,
            ScreeningStatus.CANCELLED,
        ]:
            raise ScreeningProcessCannotCancelError(current_status=process.status.value)

        # Cancel the screening
        process.status = ScreeningStatus.CANCELLED
        process.completed_at = datetime.now(timezone.utc)
        if reason:
            process.notes = reason
        process.updated_by = cancelled_by

        await self.session.flush()
        await self.session.refresh(process)

        return ScreeningProcessResponse.model_validate(process)
