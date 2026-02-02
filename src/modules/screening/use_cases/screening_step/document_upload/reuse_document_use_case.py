"""Use case for reusing an existing approved document in the screening workflow."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    DocumentNotFoundError,
    ScreeningDocumentInvalidStatusError,
    ScreeningDocumentNotFoundError,
    ScreeningDocumentReusePendingError,
    ScreeningDocumentTypeMismatchError,
    ScreeningStepNotFoundError,
    ScreeningStepNotInProgressError,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    StepStatus,
)
from src.modules.screening.domain.schemas.screening_document import (
    ScreeningDocumentResponse,
)
from src.modules.screening.infrastructure.repositories import (
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
)


class ReuseDocumentUseCase:
    """
    Reuse an existing approved document to fulfill a screening document requirement.

    This allows professionals to reuse documents they've already uploaded and had approved
    in previous screenings, rather than uploading the same document again.

    Flow:
    1. Validate ScreeningDocument exists and is PENDING_UPLOAD or CORRECTION_NEEDED
    2. Validate step is in progress
    3. Validate ProfessionalDocument exists and is not pending (already approved)
    4. Validate document type matches
    5. Link ProfessionalDocument to ScreeningDocument with PENDING_REVIEW status
    6. Update step upload count
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.step_repository = DocumentUploadStepRepository(session)
        self.document_repository = ScreeningDocumentRepository(session)
        self.professional_document_repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        screening_document_id: UUID,
        professional_document_id: UUID,
        reused_by: UUID,
    ) -> ScreeningDocumentResponse:
        """
        Reuse an existing document.

        Args:
            screening_document_id: The screening document ID.
            professional_document_id: The existing professional document to reuse.
            reused_by: User performing the reuse action.

        Returns:
            Updated screening document response.

        Raises:
            ScreeningDocumentNotFoundError: If screening document not found.
            DocumentNotFoundError: If professional document not found.
            ScreeningStepNotFoundError: If upload step not found.
            ScreeningStepNotInProgressError: If step is not in progress.
            ScreeningDocumentInvalidStatusError: If document status doesn't allow reuse.
            ScreeningDocumentReusePendingError: If professional document is pending.
            ScreeningDocumentTypeMismatchError: If document type doesn't match.
        """
        # 1. Get screening document with type
        doc = await self.document_repository.get_by_id_with_type(screening_document_id)
        if not doc:
            raise ScreeningDocumentNotFoundError(document_id=str(screening_document_id))

        # 2. Get the upload step
        step = await self.step_repository.get_by_id(doc.upload_step_id)
        if not step:
            raise ScreeningStepNotFoundError(step_id=str(doc.upload_step_id))

        # 3. Validate step is in progress or correction needed
        if step.status not in (StepStatus.IN_PROGRESS, StepStatus.CORRECTION_NEEDED):
            raise ScreeningStepNotInProgressError(
                step_id=str(step.id),
                current_status=step.status.value,
            )

        # 4. Validate document status allows reuse (same as upload)
        allowed_statuses = [
            ScreeningDocumentStatus.PENDING_UPLOAD,
            ScreeningDocumentStatus.CORRECTION_NEEDED,
        ]
        if doc.status not in allowed_statuses:
            raise ScreeningDocumentInvalidStatusError(current_status=doc.status.value)

        # 5. Validate ProfessionalDocument exists
        professional_doc = await self.professional_document_repository.get_by_id(
            professional_document_id
        )
        if not professional_doc:
            raise DocumentNotFoundError(details={"document_id": str(professional_document_id)})

        # 6. Validate document is not pending (must be an approved document)
        if professional_doc.is_pending:
            raise ScreeningDocumentReusePendingError()

        # 7. Validate document type matches
        if professional_doc.document_type_id != doc.document_type_id:
            raise ScreeningDocumentTypeMismatchError(
                expected=str(doc.document_type_id),
                found=str(professional_doc.document_type_id),
            )

        # 8. Link ProfessionalDocument to ScreeningDocument (reuse follows normal review flow)
        doc.professional_document_id = professional_document_id
        doc.status = ScreeningDocumentStatus.PENDING_REVIEW
        doc.uploaded_at = datetime.now(timezone.utc)
        doc.uploaded_by = reused_by
        doc.updated_by = reused_by

        # 9. Add to review history
        doc.review_history.append(
            {
                "user_id": str(reused_by),
                "action": "REUSE",
                "notes": f"Documento reutilizado: {professional_doc.file_name}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # 10. Clear previous rejection reason if this was a correction
        if doc.rejection_reason:
            doc.rejection_reason = None

        # 11. Update step upload count
        step.uploaded_documents = await self._count_uploaded_documents(step.id)
        step.updated_by = reused_by

        # 12. Persist changes
        await self.session.flush()
        await self.session.refresh(doc)

        # 13. Build response
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

    async def _count_uploaded_documents(self, step_id: UUID) -> int:
        """Count documents that have been uploaded or reused."""
        status_counts = await self.document_repository.count_by_status(step_id)
        # Count all documents that are not PENDING_UPLOAD or CORRECTION_NEEDED
        pending = status_counts.get(ScreeningDocumentStatus.PENDING_UPLOAD, 0)
        correction = status_counts.get(ScreeningDocumentStatus.CORRECTION_NEEDED, 0)
        total = sum(status_counts.values())
        return total - pending - correction
