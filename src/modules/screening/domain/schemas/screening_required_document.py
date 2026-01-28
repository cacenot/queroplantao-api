"""Schemas for ScreeningRequiredDocument."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.shared.domain.models import DocumentCategory
from src.modules.screening.domain.models.enums import RequiredDocumentStatus


class ReviewNoteEntry(BaseModel):
    """Schema for a single review note entry in the notes history."""

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[UUID] = Field(
        default=None,
        description="ID of the user who added the note",
    )
    text: str = Field(
        max_length=2000,
        description="Note text content",
    )
    created_at: datetime = Field(
        description="When the note was added",
    )
    action: str = Field(
        description="Action that triggered the note (UPLOAD, APPROVE, REJECT, CORRECTION, etc.)",
    )


class ScreeningRequiredDocumentCreate(BaseModel):
    """Schema for creating a required document entry (Step 2 - Document Selection)."""

    model_config = ConfigDict(from_attributes=True)

    # Use document_type_id to reference the configurable document type
    document_type_id: UUID = Field(
        description="Reference to configurable document type",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this document is mandatory",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom description for this document",
    )


class ScreeningRequiredDocumentUpdate(BaseModel):
    """Schema for updating a required document entry (PATCH)."""

    model_config = ConfigDict(from_attributes=True)

    is_required: Optional[bool] = None
    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    is_existing: Optional[bool] = None
    professional_document_id: Optional[UUID] = None


class ScreeningRequiredDocumentBulkCreate(BaseModel):
    """Schema for bulk creating required documents (Step 2 completion)."""

    model_config = ConfigDict(from_attributes=True)

    documents: list[ScreeningRequiredDocumentCreate] = Field(
        min_length=1,
        description="List of required documents to create",
    )
    step_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="General notes about document selection",
    )


class ScreeningRequiredDocumentResponse(BaseModel):
    """Schema for required document response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    process_id: UUID
    document_type_id: UUID
    is_required: bool
    description: Optional[str]
    status: RequiredDocumentStatus
    review_notes: list[dict[str, Any]]
    is_uploaded: bool
    is_existing: bool
    professional_document_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    # Document type info (from relationship)
    document_type_code: Optional[str] = None
    document_type_name: Optional[str] = None
    document_category: Optional[DocumentCategory] = None

    # Nested document type (when loaded)
    document_type: Optional["DocumentTypeListResponse"] = None


class ScreeningRequiredDocumentDetailResponse(ScreeningRequiredDocumentResponse):
    """Schema for detailed required document response with reviews."""

    reviews: Optional[list["ScreeningDocumentReviewResponse"]] = None


# Forward references
from src.modules.screening.domain.schemas.document_type import (  # noqa: E402
    DocumentTypeListResponse,
)
from src.modules.screening.domain.schemas.screening_document_review import (  # noqa: E402
    ScreeningDocumentReviewResponse,
)

ScreeningRequiredDocumentResponse.model_rebuild()
ScreeningRequiredDocumentDetailResponse.model_rebuild()
