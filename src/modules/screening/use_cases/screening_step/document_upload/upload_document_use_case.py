"""Use case for uploading a document in the document upload step."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    NotFoundError,
    ScreeningStepNotInProgressError,
)
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    StepStatus,
)
from src.modules.screening.domain.schemas.screening_document import (
    ScreeningDocumentResponse,
)
from src.modules.screening.domain.schemas.steps import UploadDocumentRequest
from src.modules.screening.infrastructure.repositories import (
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)


class UploadDocumentUseCase:
    """
    Upload a document to fulfill a screening document requirement.

    The actual file is uploaded to Firebase by the frontend.
    This use case links the ProfessionalDocument to the ScreeningDocument.

    Flow:
    1. Validate document exists and is PENDING_UPLOAD or CORRECTION_NEEDED
    2. Validate ProfessionalDocument exists
    3. Link ProfessionalDocument to ScreeningDocument
    4. Update status to PENDING_REVIEW
    5. Update step upload count
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.step_repository = DocumentUploadStepRepository(session)
        self.document_repository = ScreeningDocumentRepository(session)
        self.professional_document_repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        screening_document_id: UUID,
        data: UploadDocumentRequest,
        uploaded_by: UUID,
    ) -> ScreeningDocumentResponse:
        """
        Upload a document.

        Args:
            screening_document_id: The screening document ID.
            data: Upload data with professional_document_id.
            uploaded_by: User uploading the document.

        Returns:
            Updated screening document response.

        Raises:
            NotFoundError: If screening document or professional document not found.
            ScreeningStepNotInProgressError: If step is not in progress.
            ValidationError: If document status doesn't allow upload.
        """
        # 1. Get screening document with step
        doc = await self.document_repository.get_by_id_with_type(screening_document_id)
        if not doc:
            raise NotFoundError(
                resource="ScreeningDocument",
                identifier=str(screening_document_id),
            )

        # 2. Get the upload step
        step = await self.step_repository.get_by_id(doc.upload_step_id)
        if not step:
            raise NotFoundError(
                resource="DocumentUploadStep",
                identifier=str(doc.upload_step_id),
            )

        # 3. Validate step is in progress or correction needed
        if step.status not in (StepStatus.IN_PROGRESS, StepStatus.CORRECTION_NEEDED):
            raise ScreeningStepNotInProgressError(
                step_id=str(step.id),
                current_status=step.status.value,
            )

        # 4. Validate document status allows upload
        allowed_statuses = [
            ScreeningDocumentStatus.PENDING_UPLOAD,
            ScreeningDocumentStatus.CORRECTION_NEEDED,
        ]
        if doc.status not in allowed_statuses:
            from src.app.exceptions import ValidationError

            raise ValidationError(
                message=f"Documento não pode receber upload no status {doc.status.value}",
            )

        # 5. Validate ProfessionalDocument exists
        professional_doc = await self.professional_document_repository.get_by_id(
            data.professional_document_id
        )
        if not professional_doc:
            raise NotFoundError(
                resource="ProfessionalDocument",
                identifier=str(data.professional_document_id),
            )

        # 5.1 Validate screening_id matches if document was created for a screening
        if (
            professional_doc.screening_id is not None
            and professional_doc.screening_id != step.screening_process_id
        ):
            from src.app.exceptions import ValidationError

            raise ValidationError(
                message="Documento pertence a outro processo de triagem",
            )

        # 6. Link ProfessionalDocument to ScreeningDocument
        doc.professional_document_id = data.professional_document_id
        doc.status = ScreeningDocumentStatus.PENDING_REVIEW
        doc.uploaded_at = datetime.now(timezone.utc)
        doc.uploaded_by = uploaded_by
        doc.updated_by = uploaded_by

        # 7. Clear previous rejection reason if this is a re-upload
        if doc.rejection_reason:
            # Add to review history before clearing
            doc.review_history.append(
                {
                    "user_id": str(uploaded_by),
                    "action": "RE_UPLOAD",
                    "notes": f"Re-upload após correção. Motivo anterior: {doc.rejection_reason}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            doc.rejection_reason = None

        # 8. Update step upload count
        step.uploaded_documents = await self._count_uploaded_documents(step.id)
        step.updated_by = uploaded_by

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

    async def _count_uploaded_documents(self, step_id: UUID) -> int:
        """Count documents that have been uploaded."""
        status_counts = await self.document_repository.count_by_status(step_id)
        # Count all documents that are not PENDING_UPLOAD
        pending = status_counts.get(ScreeningDocumentStatus.PENDING_UPLOAD, 0)
        correction = status_counts.get(ScreeningDocumentStatus.CORRECTION_NEEDED, 0)
        total = sum(status_counts.values())
        return total - pending - correction
