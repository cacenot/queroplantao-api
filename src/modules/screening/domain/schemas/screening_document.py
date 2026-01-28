"""ScreeningDocument schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.screening.domain.models.enums import ScreeningDocumentStatus


class ScreeningDocumentCreate(BaseModel):
    """Schema for creating a screening document requirement."""

    model_config = ConfigDict(from_attributes=True)

    document_type_id: UUID = Field(
        description="ID of the document type",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this document is mandatory",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Display order",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom instructions for uploading",
    )


class ScreeningDocumentResponse(BaseModel):
    """Full response schema for a screening document."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    upload_step_id: UUID
    document_type_id: UUID

    # Configuration
    is_required: bool
    order: int
    description: Optional[str] = None

    # Status
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

    # Review history
    review_history: list[dict[str, Any]] = Field(default_factory=list)

    # Timestamps
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    # Computed properties (from model)
    is_uploaded: bool = False
    is_reviewed: bool = False
    is_approved: bool = False
    needs_upload: bool = True
    needs_review: bool = False
    needs_correction: bool = False
    is_complete: bool = False


class ScreeningDocumentListResponse(BaseModel):
    """Response schema for listing screening documents."""

    model_config = ConfigDict(from_attributes=True)

    documents: list[ScreeningDocumentResponse]
    total: int
    pending_upload: int
    pending_review: int
    approved: int
    correction_needed: int
