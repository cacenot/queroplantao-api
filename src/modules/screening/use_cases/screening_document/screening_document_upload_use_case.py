"""
Upload document use case.

Handles Document Upload - Professional uploads documents.
Updates ScreeningRequiredDocument status from PENDING_UPLOAD to UPLOADED.
"""

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import ProfessionalDocument
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)
from src.modules.screening.domain.models.enums import RequiredDocumentStatus
from src.modules.screening.domain.schemas import (
    ScreeningDocumentUpload,
    ScreeningRequiredDocumentResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningProcessRepository,
    ScreeningRequiredDocumentRepository,
)
from src.shared.infrastructure.repositories import DocumentTypeRepository


class UploadScreeningDocumentUseCase:
    """
    Upload a document for a screening process (Step 3).

    Creates the professional document and links it to the screening.
    Handles version increments for existing documents.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.required_document_repository = ScreeningRequiredDocumentRepository(session)
        self.professional_document_repository = ProfessionalDocumentRepository(session)
        self.doc_type_repository = DocumentTypeRepository(session)

    async def execute(
        self,
        screening_id: UUID,
        required_document_id: UUID,
        data: ScreeningDocumentUpload,
        uploaded_by: UUID | None = None,
    ) -> ScreeningRequiredDocumentResponse:
        """
        Upload a document for the screening.

        Args:
            screening_id: The screening process ID.
            required_document_id: The required document ID.
            data: Upload data including file URL.
            uploaded_by: The user uploading (None for token access).

        Returns:
            Updated required document response.

        Raises:
            NotFoundError: If screening or required document not found.
            ValidationError: If document already uploaded.
        """
        # Get the required document
        required_doc = await self.required_document_repository.get_by_id(
            required_document_id
        )
        if not required_doc or required_doc.screening_process_id != screening_id:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(
                resource="Documento requerido", identifier=str(required_document_id)
            )

        # Get the screening process
        process = await self.process_repository.get_by_id(screening_id)
        if not process:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(resource="Triagem", identifier=str(screening_id))

        # Get document type for metadata
        doc_type = await self.doc_type_repository.get_by_id(
            required_doc.document_type_config_id
        )

        # Calculate version
        version = 1
        if required_doc.professional_document_id:
            # Document already exists, increment version
            existing_doc = await self.professional_document_repository.get_by_id(
                required_doc.professional_document_id
            )
            if existing_doc:
                version = existing_doc.version + 1

        # Calculate expiration date
        expiration_date = data.expiration_date
        if not expiration_date and doc_type and doc_type.default_validity_days:
            from datetime import timedelta

            expiration_date = date.today() + timedelta(
                days=doc_type.default_validity_days
            )

        # Create professional document
        prof_doc = ProfessionalDocument(
            professional_id=process.professional_id,
            document_type=doc_type.code if doc_type else "OTHER",
            file_url=str(data.file_url),
            file_name=data.file_name,
            version=version,
            expiration_date=expiration_date,
            issuer=data.issuer,
            issue_date=data.issue_date,
            created_by=uploaded_by or process.professional_id,
            updated_by=uploaded_by or process.professional_id,
        )
        prof_doc = await self.professional_document_repository.create(prof_doc)

        # Update required document
        required_doc.professional_document_id = prof_doc.id
        required_doc.is_uploaded = True
        required_doc.is_existing = False  # New upload, not existing
        required_doc.status = RequiredDocumentStatus.UPLOADED  # Update status
        if uploaded_by:
            required_doc.updated_by = uploaded_by

        # Add note to review_notes history
        now = datetime.now(timezone.utc)
        note_entry = {
            "user_id": str(uploaded_by)
            if uploaded_by
            else str(process.professional_id),
            "text": f"Documento enviado: {data.file_name}",
            "created_at": now.isoformat(),
            "action": "UPLOAD",
        }
        required_doc.review_notes = required_doc.review_notes or []
        required_doc.review_notes.append(note_entry)

        await self.session.flush()
        await self.session.refresh(required_doc)

        return ScreeningRequiredDocumentResponse.model_validate(required_doc)


class KeepExistingDocumentUseCase:
    """
    Keep an existing professional document for screening.

    Marks the existing document as sufficient without re-upload.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.required_document_repository = ScreeningRequiredDocumentRepository(session)

    async def execute(
        self,
        screening_id: UUID,
        required_document_id: UUID,
        professional_document_id: UUID,
        updated_by: UUID | None = None,
    ) -> ScreeningRequiredDocumentResponse:
        """
        Keep an existing document without re-upload.

        Args:
            screening_id: The screening process ID.
            required_document_id: The required document ID.
            professional_document_id: The existing professional document ID.
            updated_by: The user performing the action.

        Returns:
            Updated required document response.

        Raises:
            NotFoundError: If any document not found.
        """
        # Get the required document
        required_doc = await self.required_document_repository.get_by_id(
            required_document_id
        )
        if not required_doc or required_doc.screening_process_id != screening_id:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(
                resource="Documento requerido", identifier=str(required_document_id)
            )

        # Update to keep existing
        required_doc.professional_document_id = professional_document_id
        required_doc.is_uploaded = True
        required_doc.is_existing = True
        required_doc.status = RequiredDocumentStatus.UPLOADED  # Update status
        if updated_by:
            required_doc.updated_by = updated_by

        # Add note to review_notes history
        now = datetime.now(timezone.utc)
        note_entry = {
            "user_id": str(updated_by) if updated_by else None,
            "text": "Documento existente mantido",
            "created_at": now.isoformat(),
            "action": "KEEP_EXISTING",
        }
        required_doc.review_notes = required_doc.review_notes or []
        required_doc.review_notes.append(note_entry)

        await self.session.flush()
        await self.session.refresh(required_doc)

        return ScreeningRequiredDocumentResponse.model_validate(required_doc)
