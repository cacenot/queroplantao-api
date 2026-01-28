"""Use case for reviewing a single document."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import (
    NotFoundError,
    ScreeningStepNotInProgressError,
    ValidationError,
)
from src.modules.screening.domain.models import ScreeningDocument
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    StepStatus,
)
from src.modules.screening.domain.schemas.screening_document import (
    ScreeningDocumentResponse,
)
from src.modules.screening.domain.schemas.steps import ReviewDocumentRequest
from src.modules.screening.infrastructure.repositories import (
    DocumentReviewStepRepository,
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
)


class ReviewDocumentUseCase:
    """
    Review a single document in the document review step.

    Sets the document status to APPROVED or CORRECTION_NEEDED.
    If CORRECTION_NEEDED, requires a rejection reason.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.document_repository = ScreeningDocumentRepository(session)
        self.upload_step_repository = DocumentUploadStepRepository(session)
        self.review_step_repository = DocumentReviewStepRepository(session)

    async def execute(
        self,
        screening_document_id: UUID,
        data: ReviewDocumentRequest,
        reviewed_by: UUID,
    ) -> ScreeningDocumentResponse:
        """
        Review a document.

        Args:
            screening_document_id: The screening document ID.
            data: Review data (approved, notes, rejection_reason).
            reviewed_by: User reviewing the document.

        Returns:
            Updated screening document response.

        Raises:
            NotFoundError: If document not found.
            ValidationError: If rejection without reason or document not reviewable.
            ScreeningStepNotInProgressError: If review step is not in progress.
        """
        # 1. Get document with relationships
        doc = await self._get_document_with_step(screening_document_id)
        if not doc:
            raise NotFoundError(
                resource="ScreeningDocument",
                identifier=str(screening_document_id),
            )

        # 2. Get the review step
        review_step = await self._get_review_step_for_document(doc)
        if not review_step:
            raise NotFoundError(
                resource="DocumentReviewStep",
                identifier="for document",
            )

        # 3. Validate review step is in progress
        if review_step.status != StepStatus.IN_PROGRESS:
            raise ScreeningStepNotInProgressError(
                step_id=str(review_step.id),
                current_status=review_step.status.value,
            )

        # 4. Validate document can be reviewed
        if doc.status != ScreeningDocumentStatus.PENDING_REVIEW:
            raise ValidationError(
                message=f"Documento não pode ser revisado no status {doc.status.value}",
            )

        # 5. Validate rejection has reason
        if not data.approved and not data.rejection_reason:
            raise ValidationError(
                message="Motivo da rejeição é obrigatório",
            )

        # 6. Update document status
        now = datetime.now(timezone.utc)

        if data.approved:
            doc.status = ScreeningDocumentStatus.APPROVED
            doc.rejection_reason = None
        else:
            doc.status = ScreeningDocumentStatus.CORRECTION_NEEDED
            doc.rejection_reason = data.rejection_reason

        doc.review_notes = data.notes
        doc.reviewed_at = now
        doc.reviewed_by = reviewed_by
        doc.updated_by = reviewed_by

        # 7. Add to review history
        doc.review_history.append(
            {
                "user_id": str(reviewed_by),
                "action": "APPROVED" if data.approved else "CORRECTION_NEEDED",
                "notes": data.notes,
                "rejection_reason": data.rejection_reason
                if not data.approved
                else None,
                "timestamp": now.isoformat(),
            }
        )

        # 8. Update review step counts
        review_step.update_counts()

        # 9. Persist changes
        await self.session.flush()
        await self.session.refresh(doc)

        # 10. Build response
        return ScreeningDocumentResponse(
            id=doc.id,
            upload_step_id=doc.upload_step_id,
            document_type_id=doc.document_type_id,
            is_required=doc.is_required,
            order=doc.order,
            description=doc.description,
            status=doc.status,
            professional_document_id=doc.professional_document_id,
            uploaded_at=doc.uploaded_at,
            uploaded_by=doc.uploaded_by,
            review_notes=doc.review_notes,
            rejection_reason=doc.rejection_reason,
            reviewed_at=doc.reviewed_at,
            reviewed_by=doc.reviewed_by,
            review_history=doc.review_history,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            created_by=doc.created_by,
            updated_by=doc.updated_by,
            is_uploaded=doc.is_uploaded,
            is_reviewed=doc.is_reviewed,
            is_approved=doc.is_approved,
            needs_upload=doc.needs_upload,
            needs_review=doc.needs_review,
            needs_correction=doc.needs_correction,
            is_complete=doc.is_complete,
        )

    async def _get_document_with_step(
        self,
        document_id: UUID,
    ) -> ScreeningDocument | None:
        """Get document with upload step loaded."""
        from sqlmodel import select

        query = (
            select(ScreeningDocument)
            .where(ScreeningDocument.id == document_id)
            .options(
                selectinload(ScreeningDocument.upload_step),
                selectinload(ScreeningDocument.document_type),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_review_step_for_document(
        self,
        doc: ScreeningDocument,
    ):
        """Get the review step that is linked to this document's upload step."""
        from sqlmodel import select

        from src.modules.screening.domain.models.steps import DocumentReviewStep

        query = select(DocumentReviewStep).where(
            DocumentReviewStep.upload_step_id == doc.upload_step_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
