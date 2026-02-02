"""Use case for uploading a document in the document upload step."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import Settings
from src.app.dependencies.settings import get_settings
from src.app.exceptions import (
    NotFoundError,
    ScreeningStepNotInProgressError,
    ValidationError,
)
from src.modules.professionals.domain.models import (
    DocumentSourceType,
    ProfessionalDocument,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
    ProfessionalQualificationRepository,
)
from src.modules.screening.domain.models import ScreeningProcess
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    StepStatus,
)
from src.modules.screening.domain.models.screening_document import ScreeningDocument
from src.modules.screening.domain.schemas.screening_document import (
    ScreeningDocumentResponse,
)
from src.modules.screening.infrastructure.repositories import (
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
)
from src.shared.domain.models import DocumentCategory, DocumentType
from src.shared.infrastructure.firebase import FirebaseStorageService


class UploadDocumentUseCase:
    """
    Upload a document to fulfill a screening document requirement.

    Consolidated flow:
    1. Receive file via multipart/form-data
    2. Validate ScreeningDocument and step status
    3. Upload file to Firebase Storage
    4. Create ProfessionalDocument internally (is_pending=True)
    5. Infer qualification_id and specialty_id from document category
    6. Link ProfessionalDocument to ScreeningDocument
    7. Update status to PENDING_REVIEW
    8. Update step upload count

    The backend handles the entire upload process - the frontend only needs
    to send the file in a single API call.
    """

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.step_repository = DocumentUploadStepRepository(session)
        self.document_repository = ScreeningDocumentRepository(session)
        self.professional_document_repository = ProfessionalDocumentRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)
        self.storage_service = FirebaseStorageService(self.settings)

    async def execute(
        self,
        screening_document_id: UUID,
        file: UploadFile,
        uploaded_by: UUID | None,
        *,
        expires_at: datetime | None = None,
        notes: str | None = None,
    ) -> ScreeningDocumentResponse:
        """
        Upload a document.

        Args:
            screening_document_id: The screening document ID.
            file: The uploaded file (from multipart/form-data).
            uploaded_by: User uploading the document (None for public access).
            expires_at: Optional expiration date for the document.
            notes: Optional notes about the document.

        Returns:
            Updated screening document response.

        Raises:
            NotFoundError: If screening document not found.
            ScreeningStepNotInProgressError: If step is not in progress.
            ValidationError: If document status doesn't allow upload or file is invalid.
        """
        # 1. Get screening document with document type
        doc = await self.document_repository.get_by_id_with_type(screening_document_id)
        if not doc:
            raise NotFoundError(
                resource="ScreeningDocument",
                identifier=str(screening_document_id),
            )

        # 2. Get the upload step with process
        step = await self.step_repository.get_by_id_with_process(doc.upload_step_id)
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
            raise ValidationError(
                message=f"Documento não pode receber upload no status {doc.status.value}",
            )

        # 5. Get document type for category inference
        document_type: DocumentType = doc.document_type
        process: ScreeningProcess = step.process

        # 6. Validate we have an organization_professional_id
        if not process.organization_professional_id:
            raise ValidationError(
                message="Processo de triagem não possui profissional vinculado",
            )

        # 7. Upload file to Firebase Storage
        file_size = file.size or 0
        uploaded_file = await self.storage_service.upload_file(
            file=file.file,
            file_name=file.filename or "document",
            file_size=file_size,
            content_type=file.content_type,
            organization_id=process.organization_id,
            professional_id=process.organization_professional_id,
            screening_id=process.id,
            document_type_id=doc.document_type_id,
        )

        # 8. Infer qualification_id and specialty_id based on document category
        qualification_id, specialty_id = await self._infer_document_links(
            process=process,
            document_category=document_type.category,
        )

        # 9. Create ProfessionalDocument
        professional_doc = ProfessionalDocument(
            organization_id=process.organization_id,
            organization_professional_id=process.organization_professional_id,
            document_type_id=doc.document_type_id,
            file_url=uploaded_file.url,
            file_name=file.filename or "document",
            file_size=uploaded_file.size,
            mime_type=uploaded_file.content_type,
            expires_at=expires_at,
            notes=notes,
            qualification_id=qualification_id,
            specialty_id=specialty_id,
            # Screening workflow fields
            is_pending=True,
            source_type=DocumentSourceType.SCREENING,
            screening_id=process.id,
            created_by=uploaded_by,
            updated_by=uploaded_by,
        )
        professional_doc = await self.professional_document_repository.create(
            professional_doc
        )

        # 10. Link ProfessionalDocument to ScreeningDocument
        self._link_document_to_screening(
            doc=doc,
            professional_doc=professional_doc,
            uploaded_by=uploaded_by,
        )

        # 11. Update step upload count
        step.uploaded_documents = await self._count_uploaded_documents(step.id)
        step.updated_by = uploaded_by

        # 12. Persist changes
        await self.session.flush()
        await self.session.refresh(doc)

        # 13. Build response
        return self._build_response(doc)

    async def _infer_document_links(
        self,
        process: ScreeningProcess,
        document_category: DocumentCategory,
    ) -> tuple[UUID | None, UUID | None]:
        """
        Infer qualification_id and specialty_id based on document category.

        Rules:
        - PROFILE: No links (personal documents)
        - QUALIFICATION: Link to professional's primary/first qualification
        - SPECIALTY: Link to qualification + expected_specialty_id (if doctor)

        Args:
            process: The screening process.
            document_category: The document's category.

        Returns:
            Tuple of (qualification_id, specialty_id).
        """
        qualification_id: UUID | None = None
        specialty_id: UUID | None = None

        if document_category == DocumentCategory.PROFILE:
            # Personal documents don't link to qualification/specialty
            return None, None

        # For QUALIFICATION and SPECIALTY docs, get qualification
        if process.organization_professional_id:
            qualification = await self.qualification_repository.get_first_qualification(
                professional_id=process.organization_professional_id,
            )
            if qualification:
                qualification_id = qualification.id

        # For SPECIALTY docs, also link to expected specialty
        # Doctors may not have specialty (generalista/clínico geral)
        if document_category == DocumentCategory.SPECIALTY:
            specialty_id = process.expected_specialty_id

        return qualification_id, specialty_id

    def _link_document_to_screening(
        self,
        doc: ScreeningDocument,
        professional_doc: ProfessionalDocument,
        uploaded_by: UUID | None,
    ) -> None:
        """
        Link ProfessionalDocument to ScreeningDocument and update status.

        Args:
            doc: The screening document.
            professional_doc: The created professional document.
            uploaded_by: User who uploaded.
        """
        now = datetime.now(timezone.utc)

        # Handle re-upload case
        if doc.rejection_reason:
            doc.review_history.append(
                {
                    "user_id": str(uploaded_by) if uploaded_by else None,
                    "action": "RE_UPLOAD",
                    "notes": f"Re-upload após correção. Motivo anterior: {doc.rejection_reason}",
                    "timestamp": now.isoformat(),
                }
            )
            doc.rejection_reason = None

        # Link and update status
        doc.professional_document_id = professional_doc.id
        doc.status = ScreeningDocumentStatus.PENDING_REVIEW
        doc.uploaded_at = now
        doc.uploaded_by = uploaded_by
        doc.updated_by = uploaded_by

    async def _count_uploaded_documents(self, step_id: UUID) -> int:
        """Count documents that have been uploaded."""
        status_counts = await self.document_repository.count_by_status(step_id)
        # Count all documents that are not PENDING_UPLOAD or CORRECTION_NEEDED
        pending = status_counts.get(ScreeningDocumentStatus.PENDING_UPLOAD, 0)
        correction = status_counts.get(ScreeningDocumentStatus.CORRECTION_NEEDED, 0)
        total = sum(status_counts.values())
        return total - pending - correction

    def _build_response(self, doc: ScreeningDocument) -> ScreeningDocumentResponse:
        """Build response from screening document."""
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
