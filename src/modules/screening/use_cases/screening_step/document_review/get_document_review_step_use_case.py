"""Use case for getting document review step details."""

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
from src.modules.screening.domain.models.steps import DocumentReviewStep
from src.modules.screening.domain.schemas.steps import (
    DocumentForReview,
    DocumentReviewStepResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningDocumentRepository,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models import ScreeningDocument


class GetDocumentReviewStepUseCase:
    """
    Get document review step details.

    Returns the document review step with all documents for review.
    Documents are loaded via the linked upload_step.
    Only accessible by users in the same organization (not family scope).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.document_repository = ScreeningDocumentRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> DocumentReviewStepResponse:
        """
        Get document review step with all documents.

        Args:
            organization_id: Organization ID.
            screening_id: Screening process ID.

        Returns:
            Document review step response with documents.

        Raises:
            ScreeningProcessNotFoundError: If process doesn't exist or not in org.
            ScreeningStepNotFoundError: If document review step doesn't exist.
        """
        # 1. Load process with document review step
        process = await self._load_process_with_step(organization_id, screening_id)
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # 2. Get document review step
        step = process.document_review_step
        if not step:
            raise ScreeningStepNotFoundError(step_id="document_review")

        # 3. Load documents for response (via upload_step_id)
        documents: list["ScreeningDocument"] = []
        if step.upload_step_id:
            documents = await self.document_repository.list_for_step_with_types(
                step.upload_step_id
            )

        # 4. Build response
        return self._build_response(step, documents)

    async def _load_process_with_step(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcess | None:
        """Load process with document review step (org only, no family scope)."""
        query = (
            select(ScreeningProcess)
            .where(ScreeningProcess.id == screening_id)
            .where(ScreeningProcess.organization_id == organization_id)
            .where(ScreeningProcess.deleted_at.is_(None))  # type: ignore[union-attr]
            .options(selectinload(ScreeningProcess.document_review_step))  # type: ignore[arg-type]
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _build_response(
        self,
        step: DocumentReviewStep,
        documents: list["ScreeningDocument"],
    ) -> DocumentReviewStepResponse:
        """Build response from step and documents."""
        doc_for_review = [
            DocumentForReview(
                id=doc.id,
                document_type_id=doc.document_type_id,
                document_type_name=doc.document_type.name if doc.document_type else None,
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
            for doc in documents
        ]

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
            reviewed_at=step.reviewed_at,
            completed_by=step.completed_by,
            reviewed_by=step.reviewed_by,
            upload_step_id=step.upload_step_id,
            total_to_review=step.total_to_review,
            reviewed_count=step.reviewed_count,
            approved_count=step.approved_count,
            correction_needed_count=step.correction_needed_count,
            review_progress=step.review_progress,
            all_approved=step.all_approved,
            has_corrections_needed=step.has_corrections_needed,
            documents=doc_for_review,
        )
