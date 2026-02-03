"""Document upload step - professional submits required documents."""

from typing import TYPE_CHECKING
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


class DocumentUploadStepBase(BaseModel):
    """Document upload step-specific fields."""

    # Configuration flag
    is_configured: bool = Field(
        default=False,
        description="Whether documents have been configured for this step",
    )

    # Summary counts (denormalized for quick access)
    total_documents: int = Field(
        default=0,
        ge=0,
        description="Total number of documents configured",
    )
    required_documents: int = Field(
        default=0,
        ge=0,
        description="Number of required (mandatory) documents",
    )
    uploaded_documents: int = Field(
        default=0,
        ge=0,
        description="Number of documents already uploaded",
    )


class DocumentUploadStep(DocumentUploadStepBase, ScreeningStepMixin, table=True):
    """
    Document upload step table.

    Professional uploads required documents.
    Documents are configured when the screening is created.

    The step is considered complete when:
    - All required documents are uploaded
    - Optional documents can be skipped

    After completion, the workflow moves to DocumentReviewStep.

    Workflow:
    1. Escalista configures which documents are needed (via ScreeningDocument)
    2. Professional or escalista uploads each document
    3. Each upload updates the corresponding ScreeningDocument
    4. When all required documents are uploaded, step can be completed
    """

    __tablename__ = "screening_document_upload_steps"
    __table_args__ = (
        UniqueConstraint(
            "process_id",
            name="uq_screening_document_upload_steps_process_id",
        ),
        Index("ix_screening_document_upload_steps_process_id", "process_id"),
        Index("ix_screening_document_upload_steps_status", "status"),
    )

    step_type: StepType = Field(
        default=StepType.DOCUMENT_UPLOAD,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
    )

    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="document_upload_step")
    documents: list["ScreeningDocument"] = Relationship(
        back_populates="upload_step",
        sa_relationship_kwargs={"order_by": "ScreeningDocument.order"},
    )

    # === Properties ===

    @property
    def pending_uploads(self) -> list["ScreeningDocument"]:
        """Get documents still waiting for upload."""
        return [d for d in self.documents if d.needs_upload]

    @property
    def required_pending_uploads(self) -> list["ScreeningDocument"]:
        """Get required documents still waiting for upload."""
        return [d for d in self.documents if d.is_required and d.needs_upload]

    @property
    def can_submit(self) -> bool:
        """Check if all required documents are uploaded."""
        return len(self.required_pending_uploads) == 0

    @property
    def all_required_uploaded(self) -> bool:
        """Check if all required documents have been uploaded."""
        return (
            self.required_documents == 0
            or self.uploaded_documents >= self.required_documents
        )

    @property
    def upload_progress(self) -> float:
        """Get upload progress as percentage (0-100)."""
        if self.total_documents == 0:
            return 100.0
        return (self.uploaded_documents / self.total_documents) * 100

    def update_counts(self) -> None:
        """Update denormalized counts from documents list."""
        self.total_documents = len(self.documents)
        self.required_documents = sum(1 for d in self.documents if d.is_required)
        self.uploaded_documents = sum(1 for d in self.documents if d.is_uploaded)
