"""Schemas for ScreeningDocumentReview."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.screening.domain.models.enums import DocumentReviewStatus


class ScreeningDocumentReviewCreate(BaseModel):
    """Schema for creating a document review."""

    model_config = ConfigDict(from_attributes=True)

    required_document_id: UUID = Field(
        description="The required document being reviewed",
    )
    professional_document_id: UUID = Field(
        description="The uploaded professional document being reviewed",
    )
    status: DocumentReviewStatus = Field(
        default=DocumentReviewStatus.PENDING,
        description="Initial review status",
    )


class ScreeningDocumentReviewUpdate(BaseModel):
    """Schema for updating a document review (reviewer action)."""

    model_config = ConfigDict(from_attributes=True)

    status: DocumentReviewStatus = Field(
        description="New review status",
    )
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the reviewer",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Reason for rejection (required if status=REJECTED)",
    )
    alert_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Reason for alert (required if status=ALERT)",
    )


class ScreeningDocumentReviewBulkUpdate(BaseModel):
    """Schema for bulk updating multiple document reviews."""

    model_config = ConfigDict(from_attributes=True)

    reviews: list["ScreeningDocumentReviewItemUpdate"] = Field(
        min_length=1,
        description="List of review updates",
    )
    step_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="General notes for this review session",
    )


class ScreeningDocumentReviewItemUpdate(BaseModel):
    """Schema for a single item in bulk review update."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        description="ID of the document review to update",
    )
    status: DocumentReviewStatus = Field(
        description="New status",
    )
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
    )
    alert_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
    )


class ScreeningDocumentReviewResponse(BaseModel):
    """Schema for document review response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    process_id: UUID
    process_step_id: Optional[UUID]
    required_document_id: UUID
    professional_document_id: UUID
    status: DocumentReviewStatus
    review_notes: Optional[str]
    rejection_reason: Optional[str]
    alert_reason: Optional[str]
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class ScreeningDocumentUpload(BaseModel):
    """Schema for uploading a document to a screening required document."""

    model_config = ConfigDict(from_attributes=True)

    file_url: str = Field(
        max_length=2048,
        description="Firebase Storage URL of the uploaded file",
    )
    file_name: str = Field(
        max_length=255,
        description="Original file name",
    )
    expiration_date: Optional[datetime] = Field(
        default=None,
        description="Document expiration date (if applicable)",
    )
    issue_date: Optional[datetime] = Field(
        default=None,
        description="Document issue date",
    )
    issuer: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Document issuer (e.g., 'CRM-SP')",
    )


class DocumentUploadRequest(BaseModel):
    """Schema for uploading a document during Step 3."""

    model_config = ConfigDict(from_attributes=True)

    required_document_id: UUID = Field(
        description="The required document this upload fulfills",
    )
    file_url: str = Field(
        max_length=2048,
        description="Firebase Storage URL of the uploaded file",
    )
    file_name: str = Field(
        max_length=255,
        description="Original file name",
    )
    file_size: Optional[int] = Field(
        default=None,
        ge=0,
        description="File size in bytes",
    )
    mime_type: Optional[str] = Field(
        default=None,
        max_length=100,
        description="MIME type of the file",
    )
    expiration_date: Optional[datetime] = Field(
        default=None,
        description="Document expiration date (if applicable)",
    )
    use_existing: bool = Field(
        default=False,
        description="If true, reuse existing document instead of uploading new",
    )
    existing_document_id: Optional[UUID] = Field(
        default=None,
        description="ID of existing document to reuse (if use_existing=True)",
    )


class DocumentUploadBulkRequest(BaseModel):
    """Schema for bulk uploading documents."""

    model_config = ConfigDict(from_attributes=True)

    documents: list[DocumentUploadRequest] = Field(
        min_length=1,
        description="List of documents to upload",
    )
