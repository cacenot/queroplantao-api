"""
Review document use case.

Handles Document Verification - Staff reviews uploaded documents.
Updates ScreeningRequiredDocument status and adds notes to history.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models import ScreeningDocumentReview
from src.modules.screening.domain.models.enums import (
    DocumentReviewStatus,
    RequiredDocumentStatus,
)
from src.modules.screening.domain.schemas import (
    ScreeningDocumentReviewCreate,
    ScreeningDocumentReviewResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningDocumentReviewRepository,
    ScreeningProcessRepository,
    ScreeningRequiredDocumentRepository,
)


class ReviewDocumentUseCase:
    """
    Review a screening document.

    Approves or rejects a document, updating the ScreeningRequiredDocument
    status and adding notes to the review history.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.required_document_repository = ScreeningRequiredDocumentRepository(session)
        self.review_repository = ScreeningDocumentReviewRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        required_document_id: UUID,
        data: ScreeningDocumentReviewCreate,
        reviewed_by: UUID,
    ) -> ScreeningDocumentReviewResponse:
        """
        Review a screening document.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            required_document_id: The required document ID being reviewed.
            data: Review data.
            reviewed_by: The user performing the review.

        Returns:
            The created review response.

        Raises:
            NotFoundError: If screening or document not found.
            ValidationError: If document not uploaded.
        """
        # Verify screening exists
        process = await self.process_repository.get_by_id_for_organization(
            organization_id=organization_id,
            entity_id=screening_id,
        )
        if not process:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(resource="Triagem", identifier=str(screening_id))

        # Get the required document
        required_doc = await self.required_document_repository.get_by_id(
            required_document_id
        )
        if not required_doc or required_doc.screening_process_id != screening_id:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(
                resource="Documento requerido", identifier=str(required_document_id)
            )

        # Validate document is uploaded (status must be UPLOADED or CORRECTION_NEEDED)
        if required_doc.status not in (
            RequiredDocumentStatus.UPLOADED,
            RequiredDocumentStatus.CORRECTION_NEEDED,
        ):
            from src.app.exceptions import ValidationError

            raise ValidationError(
                message="Documento ainda não foi enviado para verificação"
            )

        # Create the review record
        review = ScreeningDocumentReview(
            screening_process_id=screening_id,
            required_document_id=required_document_id,
            status=data.status,
            reviewer_id=reviewed_by,
            review_notes=data.review_notes,
            reviewed_at=datetime.now(timezone.utc),
            created_by=reviewed_by,
            updated_by=reviewed_by,
        )
        review = await self.review_repository.create(review)

        # Update ScreeningRequiredDocument status based on review result
        now = datetime.now(timezone.utc)
        if data.status == DocumentReviewStatus.APPROVED:
            required_doc.status = RequiredDocumentStatus.APPROVED
            action = "APPROVED"
        elif data.status == DocumentReviewStatus.REJECTED:
            required_doc.status = RequiredDocumentStatus.REJECTED
            action = "REJECTED"
        elif data.status == DocumentReviewStatus.ALERT:
            # Alert doesn't change the status, requires supervisor attention
            action = "ALERT"
        else:
            action = "REVIEWED"

        # Add note to review_notes history
        if data.review_notes:
            note_entry = {
                "user_id": str(reviewed_by),
                "text": data.review_notes,
                "created_at": now.isoformat(),
                "action": action,
            }
            required_doc.review_notes = required_doc.review_notes or []
            required_doc.review_notes.append(note_entry)

        await self.session.flush()

        return ScreeningDocumentReviewResponse.model_validate(review)


class ApproveDocumentUseCase:
    """Shortcut to approve a document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.review_use_case = ReviewDocumentUseCase(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        required_document_id: UUID,
        reviewed_by: UUID,
        notes: str | None = None,
    ) -> ScreeningDocumentReviewResponse:
        """Approve a document."""
        data = ScreeningDocumentReviewCreate(
            status=DocumentReviewStatus.APPROVED,
            review_notes=notes,
        )
        return await self.review_use_case.execute(
            organization_id=organization_id,
            screening_id=screening_id,
            required_document_id=required_document_id,
            data=data,
            reviewed_by=reviewed_by,
        )


class RejectDocumentUseCase:
    """Shortcut to reject a document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.review_use_case = ReviewDocumentUseCase(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        required_document_id: UUID,
        reviewed_by: UUID,
        notes: str,
    ) -> ScreeningDocumentReviewResponse:
        """Reject a document."""
        data = ScreeningDocumentReviewCreate(
            status=DocumentReviewStatus.REJECTED,
            review_notes=notes,
        )
        return await self.review_use_case.execute(
            organization_id=organization_id,
            screening_id=screening_id,
            required_document_id=required_document_id,
            data=data,
            reviewed_by=reviewed_by,
        )
