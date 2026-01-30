"""Use case for completing the document upload step."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import (
    ScreeningDocumentsNotUploadedError,
    ScreeningProcessNotFoundError,
    ScreeningStepNotFoundError,
)
from src.modules.screening.domain.models import ScreeningProcess
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    ScreeningStatus,
    StepStatus,
)
from src.modules.screening.domain.schemas.steps import (
    DocumentUploadStepCompleteRequest,
    DocumentUploadStepResponse,
    ScreeningDocumentSummary,
)
from src.modules.screening.infrastructure.repositories import (
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
    ScreeningProcessRepository,
)
from src.modules.screening.use_cases.screening_step.helpers import StepWorkflowService


class CompleteDocumentUploadStepUseCase:
    """
    Complete the document upload step.

    Validates that all required documents have been uploaded
    (status != PENDING_UPLOAD and != CORRECTION_NEEDED).

    After completion:
    - Step status becomes COMPLETED
    - DocumentReviewStep becomes IN_PROGRESS
    - Link DocumentReviewStep to this upload step
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.step_repository = DocumentUploadStepRepository(session)
        self.document_repository = ScreeningDocumentRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        data: DocumentUploadStepCompleteRequest,
        completed_by: UUID,
    ) -> DocumentUploadStepResponse:
        """
        Complete the document upload step.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.
            data: Optional notes.
            completed_by: User completing the step.

        Returns:
            Completed document upload step response.

        Raises:
            ScreeningProcessNotFoundError: If process doesn't exist.
            ScreeningStepNotFoundError: If document upload step doesn't exist.
            ScreeningDocumentsNotUploadedError: If required documents are missing.
        """
        # 1. Load process with steps
        process = await self._load_process_with_steps(organization_id, screening_id)
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get document upload step
        step = process.document_upload_step
        if not step:
            raise ScreeningStepNotFoundError(step_id="document_upload")

        # 3. Validate step can be completed
        StepWorkflowService.validate_step_can_complete(
            step=step,
            user_id=completed_by,
            check_assignment=True,
        )

        # 4. Check all required documents are uploaded
        pending_docs = await self._get_pending_required_documents(step.id)
        if pending_docs:
            doc_names = [
                doc.document_type.name if doc.document_type else str(doc.id)
                for doc in pending_docs
            ]
            raise ScreeningDocumentsNotUploadedError(document_names=doc_names)

        # 5. Save notes if provided
        if data.notes:
            step.review_notes = data.notes

        # 6. Complete the step
        StepWorkflowService.complete_step(
            step=step,
            completed_by=completed_by,
            status=StepStatus.COMPLETED,
        )

        # 7. Start process if not in progress (legacy, should not happen)
        if process.status != ScreeningStatus.IN_PROGRESS:
            process.status = ScreeningStatus.IN_PROGRESS

        # 8. Advance to document review step and link it
        review_step = process.document_review_step
        if review_step:
            review_step.upload_step_id = step.id
            review_step.update_counts()
            StepWorkflowService.advance_to_next_step(
                process=process,
                current_step=step,
                next_step=review_step,
            )

        # 9. Persist changes
        await self.session.flush()
        await self.session.refresh(step)

        # 10. Load documents for response
        documents = await self.document_repository.list_for_step_with_types(step.id)

        # 11. Build response
        return self._build_response(step, documents)

    async def _load_process_with_steps(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess | None:
        """Load process with document steps."""
        from sqlmodel import select

        query = (
            select(ScreeningProcess)
            .where(ScreeningProcess.id == screening_id)
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))
            .options(
                selectinload(ScreeningProcess.document_upload_step),
                selectinload(ScreeningProcess.document_review_step),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_pending_required_documents(
        self,
        step_id: UUID,
    ) -> list:
        """Get required documents that haven't been uploaded."""
        from sqlmodel import select

        from src.modules.screening.domain.models import ScreeningDocument

        pending_statuses = [
            ScreeningDocumentStatus.PENDING_UPLOAD,
            ScreeningDocumentStatus.CORRECTION_NEEDED,
        ]
        query = (
            select(ScreeningDocument)
            .where(ScreeningDocument.upload_step_id == step_id)
            .where(ScreeningDocument.is_required.is_(True))
            .where(ScreeningDocument.status.in_(pending_statuses))
            .options(selectinload(ScreeningDocument.document_type))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    def _build_response(
        self,
        step,
        documents: list,
    ) -> DocumentUploadStepResponse:
        """Build response with documents summary."""
        doc_summaries = []
        for doc in documents:
            summary = ScreeningDocumentSummary(
                id=doc.id,
                document_type_id=doc.document_type_id,
                document_type_name=doc.document_type.name
                if doc.document_type
                else None,
                is_required=doc.is_required,
                order=doc.order,
                status=doc.status.value,
                is_uploaded=doc.is_uploaded,
                uploaded_at=doc.uploaded_at,
            )
            doc_summaries.append(summary)

        return DocumentUploadStepResponse(
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
            total_documents=step.total_documents,
            required_documents=step.required_documents,
            uploaded_documents=step.uploaded_documents,
            upload_progress=step.upload_progress,
            all_required_uploaded=step.all_required_uploaded,
            documents=doc_summaries,
        )
