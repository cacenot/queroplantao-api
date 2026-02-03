"""Use case for getting document upload step details."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.app.exceptions import (
    ScreeningProcessNotFoundError,
    ScreeningStepNotFoundError,
)
from src.modules.screening.domain.models import ScreeningProcess
from src.modules.screening.domain.models.steps import DocumentUploadStep
from src.modules.screening.domain.schemas.steps import (
    DocumentUploadStepResponse,
    ScreeningDocumentSummary,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningDocumentRepository,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models import ScreeningDocument


class GetDocumentUploadStepUseCase:
    """
    Get document upload step details.

    Returns the document upload step with all documents and their types.
    Only accessible by users in the same organization (not family scope).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.document_repository = ScreeningDocumentRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> DocumentUploadStepResponse:
        """
        Get document upload step with all documents.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.

        Returns:
            Document upload step response with documents.

        Raises:
            ScreeningProcessNotFoundError: If process doesn't exist or not in org.
            ScreeningStepNotFoundError: If document upload step doesn't exist.
        """
        # 1. Load process with document upload step
        process = await self._load_process_with_step(organization_id, screening_id)
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get document upload step
        step = process.document_upload_step
        if not step:
            raise ScreeningStepNotFoundError(step_id="document_upload")

        # 3. Load documents for response
        documents = await self.document_repository.list_for_step_with_types(step.id)

        # 4. Build response
        return self._build_response(step, documents)

    async def _load_process_with_step(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess | None:
        """Load process with document upload step (org only, no family scope)."""
        query = (
            select(ScreeningProcess)
            .where(ScreeningProcess.id == screening_id)
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))  # type: ignore[union-attr]
            .options(selectinload(ScreeningProcess.document_upload_step))  # type: ignore[arg-type]
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _build_response(
        self,
        step: DocumentUploadStep,
        documents: list["ScreeningDocument"],
    ) -> DocumentUploadStepResponse:
        """Build response from step and documents."""
        doc_summaries = [
            ScreeningDocumentSummary(
                id=doc.id,
                document_type_id=doc.document_type_id,
                document_type_name=doc.document_type.name if doc.document_type else None,
                is_required=doc.is_required,
                order=doc.order,
                status=doc.status.value,
                is_uploaded=doc.is_uploaded,
                uploaded_at=doc.uploaded_at,
            )
            for doc in documents
        ]

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
            reviewed_at=step.reviewed_at,
            completed_by=step.completed_by,
            reviewed_by=step.reviewed_by,
            is_configured=step.is_configured,
            total_documents=step.total_documents,
            required_documents=step.required_documents,
            uploaded_documents=step.uploaded_documents,
            upload_progress=step.upload_progress,
            all_required_uploaded=step.all_required_uploaded,
            documents=doc_summaries,
        )
