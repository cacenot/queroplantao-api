"""ScreeningDocument model - documents in a screening workflow."""

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import ScreeningDocumentStatus
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_document import (
        ProfessionalDocument,
    )
    from src.modules.screening.domain.models.steps.document_upload_step import (
        DocumentUploadStep,
    )
    from src.shared.domain.models import DocumentType


class ScreeningDocumentBase(BaseModel):
    """Base fields for ScreeningDocument."""

    # Configuration
    is_required: bool = Field(
        default=True,
        description="Whether this document is mandatory",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Display order within the upload step",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom instructions for uploading this document",
    )

    # Current status
    status: ScreeningDocumentStatus = Field(
        default=ScreeningDocumentStatus.PENDING_UPLOAD,
        description="Current status in the workflow",
    )

    # Review data (filled during DOCUMENT_REVIEW step)
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the reviewer",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Reason for rejection (if CORRECTION_NEEDED)",
    )

    # Review history - JSONB array of {user_id, action, notes, timestamp}
    review_history: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_type=JSONB,
        description="Audit trail of review actions",
    )


class ScreeningDocument(
    ScreeningDocumentBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ScreeningDocument table model.

    Represents a document requirement within a screening workflow.
    Tracks the full lifecycle: requirement → upload → review.

    This model unifies what was previously split between:
    - ScreeningRequiredDocument (the requirement)
    - ScreeningDocumentReview (the review)

    Lifecycle:
    1. Created with PENDING_UPLOAD when documents are configured
    2. Moves to PENDING_REVIEW when professional uploads (links professional_document_id)
    3. Reviewer sets APPROVED or CORRECTION_NEEDED
    4. If CORRECTION_NEEDED, professional re-uploads and status goes back to PENDING_REVIEW

    For optional documents:
    - is_required=False
    - Can be SKIPPED if not provided
    - Still goes through review if uploaded

    For reused documents:
    - REUSED status when document from previous screening is used
    """

    __tablename__ = "screening_documents"
    __table_args__ = (
        # Each document type can only appear once per upload step
        UniqueConstraint(
            "upload_step_id",
            "document_type_id",
            name="uq_screening_documents_step_doc_type",
        ),
        # Index for listing by step
        Index("ix_screening_documents_upload_step_id", "upload_step_id"),
        # Index for filtering by status
        Index("ix_screening_documents_status", "status"),
        # Index for document type
        Index("ix_screening_documents_document_type_id", "document_type_id"),
    )

    # Parent step reference (the DOCUMENT_UPLOAD step)
    upload_step_id: UUID = Field(
        foreign_key="screening_document_upload_steps.id",
        nullable=False,
        description="The document upload step this belongs to",
    )

    # Document type reference
    document_type_id: UUID = Field(
        foreign_key="document_types.id",
        nullable=False,
        description="Reference to the document type configuration",
    )

    # The actual uploaded document (set when professional uploads)
    professional_document_id: Optional[UUID] = Field(
        default=None,
        foreign_key="professional_documents.id",
        nullable=True,
        description="The uploaded document fulfilling this requirement",
    )

    # Upload tracking
    uploaded_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the document was uploaded",
    )
    uploaded_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="Who uploaded the document (no FK - follows TrackingMixin pattern)",
    )

    # Review tracking
    reviewed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the document was last reviewed",
    )
    reviewed_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="Who reviewed the document (no FK - follows TrackingMixin pattern)",
    )

    # Relationships
    upload_step: "DocumentUploadStep" = Relationship(
        back_populates="documents",
    )
    document_type: "DocumentType" = Relationship(
        back_populates="screening_documents",
    )
    professional_document: Optional["ProfessionalDocument"] = Relationship()

    # === Properties ===

    @property
    def is_uploaded(self) -> bool:
        """Check if document has been uploaded."""
        return self.professional_document_id is not None

    @property
    def is_reviewed(self) -> bool:
        """Check if document has been reviewed."""
        return self.status in (
            ScreeningDocumentStatus.APPROVED,
            ScreeningDocumentStatus.CORRECTION_NEEDED,
        )

    @property
    def is_approved(self) -> bool:
        """Check if document is approved."""
        return self.status == ScreeningDocumentStatus.APPROVED

    @property
    def needs_upload(self) -> bool:
        """Check if document still needs to be uploaded."""
        return self.status == ScreeningDocumentStatus.PENDING_UPLOAD

    @property
    def needs_review(self) -> bool:
        """Check if document is waiting for review."""
        return self.status == ScreeningDocumentStatus.PENDING_REVIEW

    @property
    def needs_correction(self) -> bool:
        """Check if document needs re-upload after rejection."""
        return self.status == ScreeningDocumentStatus.CORRECTION_NEEDED

    @property
    def is_reused(self) -> bool:
        """Check if document is reused from previous screening."""
        return self.status == ScreeningDocumentStatus.REUSED

    @property
    def is_skipped(self) -> bool:
        """Check if optional document was skipped."""
        return self.status == ScreeningDocumentStatus.SKIPPED

    @property
    def is_complete(self) -> bool:
        """Check if document requirement is satisfied."""
        if not self.is_required:
            return self.status in (
                ScreeningDocumentStatus.APPROVED,
                ScreeningDocumentStatus.SKIPPED,
                ScreeningDocumentStatus.REUSED,
            )
        return self.status in (
            ScreeningDocumentStatus.APPROVED,
            ScreeningDocumentStatus.REUSED,
        )
