"""ScreeningDocumentReview model - individual document verification."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import DocumentReviewStatus
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_document import (
        ProfessionalDocument,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess
    from src.modules.screening.domain.models.screening_process_step import (
        ScreeningProcessStep,
    )
    from src.modules.screening.domain.models.screening_required_document import (
        ScreeningRequiredDocument,
    )


class ScreeningDocumentReviewBase(BaseModel):
    """Base fields for ScreeningDocumentReview."""

    status: DocumentReviewStatus = Field(
        default=DocumentReviewStatus.PENDING,
        sa_type=SAEnum(
            DocumentReviewStatus,
            name="document_review_status",
            create_constraint=True,
        ),
        description="Current review status of this document",
    )
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="General notes/feedback from the reviewer",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Specific reason for rejection (if rejected)",
    )
    alert_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Reason for alert flag (if alert status)",
    )


class ScreeningDocumentReview(
    ScreeningDocumentReviewBase,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ScreeningDocumentReview table model.

    Tracks the verification status of each individual document uploaded
    during a screening process.

    Each document can be:
    - PENDING: Not yet reviewed
    - APPROVED: Document is valid and accepted
    - REJECTED: Document is invalid, illegible, or incorrect - needs re-upload
    - ALERT: Document raises concerns requiring supervisor attention

    When any document is REJECTED:
    - The screening returns to PENDING_CORRECTION status
    - The professional/escalista must correct and re-upload

    When any document has ALERT:
    - The screening moves to ESCALATED status
    - A supervisor must review and make final decision

    Review process:
    1. Escalista creates screening and specifies required documents
    2. Professional/escalista uploads documents during DOCUMENTS step
    3. Gestor reviews each document in DOCUMENT_REVIEW step
    4. Each document gets individual status (APPROVED/REJECTED/ALERT)
    5. Based on document statuses, screening proceeds or goes back
    """

    __tablename__ = "screening_document_reviews"
    __table_args__ = (
        # Each professional document can only be reviewed once per process
        UniqueConstraint(
            "process_id",
            "professional_document_id",
            name="uq_screening_doc_reviews_process_prof_doc",
        ),
        # Index for listing reviews by process
        Index("ix_screening_document_reviews_process_id", "process_id"),
        # Index for listing reviews by step
        Index("ix_screening_document_reviews_step_id", "process_step_id"),
        # Index for filtering by status
        Index("ix_screening_document_reviews_status", "status"),
    )

    # Process reference
    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
        description="Screening process this review belongs to",
    )

    # Process step reference (should be DOCUMENT_REVIEW step)
    process_step_id: Optional[UUID] = Field(
        default=None,
        foreign_key="screening_process_steps.id",
        nullable=True,
        description="The DOCUMENT_REVIEW step this review was created in",
    )

    # Professional document being reviewed
    professional_document_id: UUID = Field(
        foreign_key="professional_documents.id",
        nullable=False,
        description="The uploaded document being reviewed",
    )

    # Optional link to required document specification
    required_document_id: Optional[UUID] = Field(
        default=None,
        foreign_key="screening_required_documents.id",
        nullable=True,
        description="The required document this fulfills (if applicable)",
    )

    # Review timestamps
    reviewed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this document was reviewed",
    )
    reviewed_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who reviewed this document",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="document_reviews")
    process_step: Optional["ScreeningProcessStep"] = Relationship(
        back_populates="document_reviews",
    )
    professional_document: "ProfessionalDocument" = Relationship()
    required_document: Optional["ScreeningRequiredDocument"] = Relationship(
        back_populates="reviews",
    )

    @property
    def is_reviewed(self) -> bool:
        """Check if this document has been reviewed."""
        return self.status != DocumentReviewStatus.PENDING

    @property
    def is_approved(self) -> bool:
        """Check if this document was approved."""
        return self.status == DocumentReviewStatus.APPROVED

    @property
    def needs_attention(self) -> bool:
        """Check if this document needs attention (rejected or alert)."""
        return self.status in (
            DocumentReviewStatus.REJECTED,
            DocumentReviewStatus.ALERT,
        )

    @property
    def requires_escalation(self) -> bool:
        """Check if this document requires escalation to supervisor."""
        return self.status == DocumentReviewStatus.ALERT
