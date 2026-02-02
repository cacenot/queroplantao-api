"""Use case for completing the document review step."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import (
    ScreeningDocumentsPendingReviewError,
    ScreeningProcessNotFoundError,
    ScreeningStepNotFoundError,
)
from src.modules.screening.domain.models import ScreeningProcess
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.schemas.steps import (
    DocumentForReview,
    DocumentReviewStepCompleteRequest,
    DocumentReviewStepResponse,
)
from src.modules.screening.infrastructure.repositories import (
    DocumentReviewStepRepository,
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
    ScreeningProcessRepository,
)
from src.modules.screening.use_cases.screening_step.helpers import StepWorkflowService


class CompleteDocumentReviewStepUseCase:
    """
    Complete the document review step.

    Validates that all documents have been reviewed (no PENDING_REVIEW).

    Outcomes:
    - All APPROVED: Step is APPROVED, advance to next step
    - Any CORRECTION_NEEDED: Step is CORRECTION_NEEDED, go back to upload step

    Correction cycle:
    1. Documents with CORRECTION_NEEDED stay that way
    2. DocumentUploadStep goes to CORRECTION_NEEDED
    3. Professional re-uploads documents
    4. After all uploaded, DocumentUploadStep.complete() called again
    5. DocumentReviewStep goes back to IN_PROGRESS
    6. Reviewer reviews again
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.review_step_repository = DocumentReviewStepRepository(session)
        self.upload_step_repository = DocumentUploadStepRepository(session)
        self.document_repository = ScreeningDocumentRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        data: DocumentReviewStepCompleteRequest,
        completed_by: UUID,
    ) -> DocumentReviewStepResponse:
        """
        Complete the document review step.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.
            data: Optional notes.
            completed_by: User completing the step.

        Returns:
            Completed document review step response.

        Raises:
            ScreeningProcessNotFoundError: If process doesn't exist.
            ScreeningStepNotFoundError: If document review step doesn't exist.
            ScreeningDocumentsPendingReviewError: If documents still pending.
        """
        # 1. Load process with steps
        process = await self._load_process_with_steps(organization_id, screening_id)
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get document review step
        review_step = process.document_review_step
        if not review_step:
            raise ScreeningStepNotFoundError(step_id="document_review")

        # 3. Validate step can be completed
        StepWorkflowService.validate_step_can_complete(
            step=review_step,
            user_id=completed_by,
            check_assignment=True,
        )

        # 4. Get documents for this step
        documents = await self.document_repository.list_for_step_with_types(
            review_step.upload_step_id
        )

        # 5. Check no documents are pending review
        pending_review = [
            d for d in documents if d.status == ScreeningDocumentStatus.PENDING_REVIEW
        ]
        if pending_review:
            doc_names = [
                doc.document_type.name if doc.document_type else str(doc.id)
                for doc in pending_review
            ]
            raise ScreeningDocumentsPendingReviewError(document_names=doc_names)

        # 6. Save notes if provided
        if data.notes:
            review_step.review_notes = data.notes

        # 7. Update counts
        review_step.update_counts()

        # 8. Determine outcome based on document statuses
        has_corrections = any(
            d.status == ScreeningDocumentStatus.CORRECTION_NEEDED for d in documents
        )

        if has_corrections:
            # Go back to upload step for corrections
            await self._handle_correction_cycle(
                process=process,
                review_step=review_step,
                documents=documents,
                completed_by=completed_by,
            )
        else:
            # All approved - complete and advance
            StepWorkflowService.complete_step(
                step=review_step,
                completed_by=completed_by,
                status=StepStatus.APPROVED,
                process=process,
            )

            # Determine and start next step
            next_step = self._get_next_step(process)
            StepWorkflowService.advance_to_next_step(
                process=process,
                current_step=review_step,
                next_step=next_step,
            )

        # 9. Persist changes
        await self.session.flush()
        await self.session.refresh(review_step)

        # 10. Build response
        return self._build_response(review_step, documents)

    async def _handle_correction_cycle(
        self,
        process: ScreeningProcess,
        review_step,
        documents: list,
        completed_by: UUID,
    ) -> None:
        """
        Handle the correction cycle when documents need re-upload.

        1. Set review step to CORRECTION_NEEDED
        2. Set upload step to CORRECTION_NEEDED
        3. Documents with CORRECTION_NEEDED stay that way (already set by reviewer)
        """
        now = datetime.now(timezone.utc)

        # Mark review step as needing correction
        review_step.status = StepStatus.CORRECTION_NEEDED
        review_step.completed_at = now
        review_step.completed_by = completed_by

        # Get upload step and mark it as needing correction
        upload_step = process.document_upload_step
        if upload_step:
            upload_step.status = StepStatus.CORRECTION_NEEDED
            StepWorkflowService.update_step_status(process, upload_step)

        StepWorkflowService.update_step_status(process, review_step)
        StepWorkflowService.set_current_step(process, StepType.DOCUMENT_UPLOAD)

    async def _load_process_with_steps(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess | None:
        """Load process with document steps and potential next steps."""
        from sqlmodel import select

        query = (
            select(ScreeningProcess)
            .where(ScreeningProcess.id == screening_id)
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))
            .options(
                selectinload(ScreeningProcess.document_upload_step),
                selectinload(ScreeningProcess.document_review_step),
                selectinload(ScreeningProcess.payment_info_step),
                selectinload(ScreeningProcess.client_validation_step),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _get_next_step(self, process: ScreeningProcess):
        """Get the next step after document review based on configuration."""
        from src.modules.screening.domain.models.enums import StepType

        configured = process.configured_step_types
        try:
            current_idx = configured.index(StepType.DOCUMENT_REVIEW.value)
        except ValueError:
            return None

        next_idx = current_idx + 1
        if next_idx >= len(configured):
            return None

        next_type = configured[next_idx]

        if next_type == StepType.PAYMENT_INFO.value:
            return process.payment_info_step
        elif next_type == StepType.CLIENT_VALIDATION.value:
            return process.client_validation_step

        return None

    def _build_response(
        self,
        step,
        documents: list,
    ) -> DocumentReviewStepResponse:
        """Build response with documents."""
        doc_responses = []
        for doc in documents:
            doc_resp = DocumentForReview(
                id=doc.id,
                document_type_id=doc.document_type_id,
                document_type_name=doc.document_type.name
                if doc.document_type
                else None,
                is_required=doc.is_required,
                order=doc.order,
                status=doc.status,
                professional_document_id=doc.professional_document_id,
                uploaded_at=doc.uploaded_at,
                uploaded_by=doc.uploaded_by,
                review_notes=doc.review_notes,
                rejection_reason=doc.rejection_reason,
                reviewed_at=doc.reviewed_at,
                reviewed_by=doc.reviewed_by,
            )
            doc_responses.append(doc_resp)

        return DocumentReviewStepResponse(
            id=step.id,
            step_type=step.step_type,
            order=step.order,
            status=step.status,
            assigned_to=step.assigned_to,
            review_notes=step.review_notes,
            rejection_reason=step.rejection_reason,
            created_at=step.created_at,
            updated_at=step.updated_at,
            started_at=step.started_at,
            completed_at=step.completed_at,
            completed_by=step.completed_by,
            reviewed_at=step.reviewed_at,
            reviewed_by=step.reviewed_by,
            upload_step_id=step.upload_step_id,
            total_to_review=step.total_to_review,
            reviewed_count=step.reviewed_count,
            approved_count=step.approved_count,
            correction_needed_count=step.correction_needed_count,
            review_progress=step.review_progress,
            all_approved=step.all_approved,
            has_corrections_needed=step.has_corrections_needed,
            documents=doc_responses,
        )
