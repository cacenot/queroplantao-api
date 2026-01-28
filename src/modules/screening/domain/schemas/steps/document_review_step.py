"""Document review step schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.screening.domain.models.enums import ScreeningDocumentStatus
from src.modules.screening.domain.schemas.steps.base import StepResponseBase


class ReviewDocumentRequest(BaseModel):
    """Request schema for reviewing a single document."""

    model_config = ConfigDict(from_attributes=True)

    approved: bool = Field(
        description="True to approve, False to request correction",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional notes from the reviewer",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Required reason if rejecting (approved=False)",
    )


class DocumentReviewStepCompleteRequest(BaseModel):
    """Request schema for completing document review step.

    This step is completed when all documents have been reviewed.
    The system validates that no documents have status = PENDING_REVIEW.
    """

    model_config = ConfigDict(from_attributes=True)

    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional notes about the review",
    )


class DocumentForReview(BaseModel):
    """Document information for review step response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type_id: UUID
    document_type_name: Optional[str] = None
    is_required: bool
    order: int
    status: ScreeningDocumentStatus

    # Upload info
    professional_document_id: Optional[UUID] = None
    uploaded_at: Optional[datetime] = None
    uploaded_by: Optional[UUID] = None

    # Review info
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[UUID] = None


class DocumentReviewStepResponse(StepResponseBase):
    """
    Response schema for document review step.

    Includes review counts and document list.
    """

    # Reference to upload step
    upload_step_id: Optional[UUID] = None

    # Review counts (denormalized)
    total_to_review: int = 0
    reviewed_count: int = 0
    approved_count: int = 0
    correction_needed_count: int = 0

    # Progress
    review_progress: float = 0.0
    all_approved: bool = False
    has_corrections_needed: bool = False

    # Documents to review
    documents: list[DocumentForReview] = Field(default_factory=list)
