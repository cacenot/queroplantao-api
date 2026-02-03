"""Use case for configuring documents in document upload step."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import (
    ScreeningProcessNotFoundError,
    ScreeningStepNotFoundError,
    ScreeningStepNotPendingError,
)
from src.modules.screening.domain.models import ScreeningDocument, ScreeningProcess
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    ScreeningStatus,
    StepStatus,
)
from src.modules.screening.domain.models.steps import DocumentUploadStep
from src.modules.screening.domain.schemas.steps import (
    ConfigureDocumentsRequest,
    DocumentUploadStepResponse,
    ScreeningDocumentSummary,
)
from src.modules.screening.infrastructure.repositories import (
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
    ScreeningProcessRepository,
)
from src.modules.screening.use_cases.screening_step.helpers import StepWorkflowService
from src.shared.domain.models import DocumentType
from src.shared.infrastructure.repositories import DocumentTypeRepository


class ConfigureDocumentsUseCase:
    """
    Configure documents for the document upload step.

    This use case creates ScreeningDocument records for each document
    that the professional needs to upload.

    The step transitions from PENDING to IN_PROGRESS after configuration
    (or stays IN_PROGRESS if already started).

    Validations:
    - Process must exist and belong to organization
    - Document upload step must exist for the process
    - Step must be PENDING or IN_PROGRESS
    - All document types must exist
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.step_repository = DocumentUploadStepRepository(session)
        self.document_repository = ScreeningDocumentRepository(session)
        self.document_type_repository = DocumentTypeRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        data: ConfigureDocumentsRequest,
        configured_by: UUID,
    ) -> DocumentUploadStepResponse:
        """
        Configure documents for the upload step.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.
            data: List of documents to configure.
            configured_by: User configuring the documents.

        Returns:
            Updated document upload step response.

        Raises:
            ScreeningProcessNotFoundError: If process doesn't exist.
            ScreeningStepNotFoundError: If document upload step doesn't exist.
            ScreeningStepNotPendingError: If step is not PENDING or IN_PROGRESS.
            NotFoundError: If any document type doesn't exist.
        """
        # 1. Load process with steps
        process = await self._load_process_with_steps(organization_id, screening_id)
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get document upload step
        step = process.document_upload_step
        if not step:
            raise ScreeningStepNotFoundError(step_id="document_upload")

        # 3. Validate step is PENDING or IN_PROGRESS
        if step.status not in (StepStatus.PENDING, StepStatus.IN_PROGRESS):
            raise ScreeningStepNotPendingError(
                step_id=str(step.id),
                current_status=step.status.value,
            )

        # 4. Validate all document types exist
        doc_type_ids = [d.document_type_id for d in data.documents]
        doc_types = await self.document_type_repository.get_by_ids(doc_type_ids)
        doc_type_map = {dt.id: dt for dt in doc_types}

        missing_types = set(doc_type_ids) - set(doc_type_map.keys())
        if missing_types:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(
                resource="DocumentType",
                identifier=str(list(missing_types)[0]),
            )

        # 5. Create ScreeningDocument records
        documents: list[ScreeningDocument] = []
        for item in data.documents:
            doc = ScreeningDocument(
                upload_step_id=step.id,
                document_type_id=item.document_type_id,
                is_required=item.is_required,
                order=item.order,
                description=item.description,
                status=ScreeningDocumentStatus.PENDING_UPLOAD,
                created_by=configured_by,
            )
            documents.append(doc)

        await self.document_repository.bulk_create(documents)

        # 6. Update step to IN_PROGRESS if it was PENDING
        if step.status == StepStatus.PENDING:
            step.status = StepStatus.IN_PROGRESS
            step.started_at = datetime.now(timezone.utc)
            StepWorkflowService.update_step_status(process, step)

        # 7. Update step counts
        step.total_documents = len(documents)
        step.required_documents = sum(1 for d in documents if d.is_required)
        step.uploaded_documents = 0

        # 8. Start process
        process.status = ScreeningStatus.IN_PROGRESS

        # 9. Persist changes
        await self.session.flush()
        await self.session.refresh(step)

        # 10. Build response
        return self._build_response(step, documents, doc_type_map)

    async def _load_process_with_steps(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess | None:
        """Load process with document upload step."""
        from sqlmodel import select

        query = (
            select(ScreeningProcess)
            .where(ScreeningProcess.id == screening_id)
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))
            .options(
                selectinload(ScreeningProcess.document_upload_step),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _build_response(
        self,
        step: DocumentUploadStep,
        documents: list[ScreeningDocument],
        doc_type_map: dict[UUID, DocumentType],
    ) -> DocumentUploadStepResponse:
        """Build response with documents summary."""
        all_required_uploaded = (
            step.required_documents == 0
            or step.uploaded_documents >= step.required_documents
        )
        doc_summaries = []
        for doc in documents:
            doc_type = doc_type_map.get(doc.document_type_id)
            summary = ScreeningDocumentSummary(
                id=doc.id,
                document_type_id=doc.document_type_id,
                document_type_name=doc_type.name if doc_type else None,
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
            all_required_uploaded=all_required_uploaded,
            documents=doc_summaries,
        )
