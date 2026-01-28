"""Document review step - internal verification of uploaded documents."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import StepType
from src.modules.screening.domain.models.steps.base_step import ScreeningStepMixin
from src.shared.domain.models.base import BaseModel

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_document import (
        ScreeningDocument,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess
    from src.modules.screening.domain.models.steps.document_upload_step import (
        DocumentUploadStep,
    )


class DocumentReviewStepBase(BaseModel):
    """Document review step-specific fields."""

    # Summary counts (denormalized for quick access)
    total_to_review: int = Field(
        default=0,
        ge=0,
        description="Total documents to review",
    )
    reviewed_count: int = Field(
        default=0,
        ge=0,
        description="Documents reviewed so far",
    )
    approved_count: int = Field(
        default=0,
        ge=0,
        description="Documents approved",
    )
    rejected_count: int = Field(
        default=0,
        ge=0,
        description="Documents rejected (need re-upload)",
    )
    alert_count: int = Field(
        default=0,
        ge=0,
        description="Documents with alerts (need supervisor)",
    )


class DocumentReviewStep(DocumentReviewStepBase, ScreeningStepMixin, table=True):
    """
    Document review step table.

    Internal user reviews each uploaded document.

    The step completes when all uploaded documents have been reviewed.
    Based on review outcomes:
    - All APPROVED → screening continues to next step
    - Any REJECTED → step gets CORRECTION_NEEDED, back to upload step
    - Any ALERT → triggers SupervisorReviewStep (if configured)

    Documents are accessed via the linked DocumentUploadStep.

    Workflow:
    1. Gestor opens document review step
    2. Reviews each document individually
    3. Sets status for each: APPROVED, REJECTED (with reason), or ALERT
    4. When all reviewed, determines next action based on outcomes
    """

    __tablename__ = "screening_document_review_steps"
    __table_args__ = (
        UniqueConstraint(
            "process_id",
            name="uq_screening_document_review_steps_process_id",
        ),
        Index("ix_screening_document_review_steps_process_id", "process_id"),
        Index("ix_screening_document_review_steps_status", "status"),
    )

    step_type: StepType = Field(
        default=StepType.DOCUMENT_REVIEW,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
    )

    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
    )

    # Reference to the upload step (to access documents)
    upload_step_id: Optional[UUID] = Field(
        default=None,
        foreign_key="screening_document_upload_steps.id",
        nullable=True,
        description="The upload step whose documents are being reviewed",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="document_review_step")
    upload_step: Optional["DocumentUploadStep"] = Relationship()

    # === Properties ===

    @property
    def documents(self) -> list["ScreeningDocument"]:
        """Get documents to review (via upload step)."""
        if self.upload_step:
            return self.upload_step.documents
        return []

    @property
    def pending_review(self) -> list["ScreeningDocument"]:
        """Get documents waiting for review."""
        return [d for d in self.documents if d.needs_review]

    @property
    def has_rejections(self) -> bool:
        """Check if any document was rejected."""
        return self.rejected_count > 0

    @property
    def has_alerts(self) -> bool:
        """Check if any document has alerts."""
        return self.alert_count > 0

    @property
    def all_approved(self) -> bool:
        """Check if all documents are approved."""
        return (
            self.reviewed_count == self.total_to_review
            and self.rejected_count == 0
            and self.alert_count == 0
        )

    @property
    def review_progress(self) -> float:
        """Get review progress as percentage (0-100)."""
        if self.total_to_review == 0:
            return 100.0
        return (self.reviewed_count / self.total_to_review) * 100

    def update_counts(self) -> None:
        """Update denormalized counts from documents."""
        docs = self.documents
        self.total_to_review = sum(1 for d in docs if d.is_uploaded)
        self.reviewed_count = sum(1 for d in docs if d.is_reviewed)
        self.approved_count = sum(1 for d in docs if d.is_approved)
        self.rejected_count = sum(1 for d in docs if d.needs_correction)
        self.alert_count = sum(1 for d in docs if d.requires_escalation)
