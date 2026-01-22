"""Schemas for ProfessionalDocument."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from src.modules.professionals.domain.models import DocumentCategory, DocumentType


class ProfessionalDocumentCreate(BaseModel):
    """Schema for creating a professional document."""

    model_config = ConfigDict(from_attributes=True)

    document_type: DocumentType = Field(
        description="Type of document (ID_DOCUMENT, DIPLOMA, etc.)",
    )
    document_category: DocumentCategory = Field(
        description="Category: PROFILE, QUALIFICATION, or SPECIALTY",
    )
    file_url: str = Field(
        max_length=2048,
        description="URL to the uploaded file",
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
    expires_at: Optional[AwareDatetime] = Field(
        default=None,
        description="Expiration date for documents with validity",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about this document",
    )

    # Optional links for QUALIFICATION and SPECIALTY category documents
    qualification_id: Optional[UUID] = Field(
        default=None,
        description="Professional qualification ID (for QUALIFICATION category)",
    )
    specialty_id: Optional[UUID] = Field(
        default=None,
        description="Professional specialty ID (for SPECIALTY category)",
    )


class ProfessionalDocumentUpdate(BaseModel):
    """Schema for updating a professional document (PATCH - partial update)."""

    model_config = ConfigDict(from_attributes=True)

    file_url: Optional[str] = Field(
        default=None,
        max_length=2048,
        description="URL to the uploaded file",
    )
    file_name: Optional[str] = Field(
        default=None,
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
    expires_at: Optional[AwareDatetime] = Field(
        default=None,
        description="Expiration date for documents with validity",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about this document",
    )


class ProfessionalDocumentResponse(BaseModel):
    """Schema for professional document response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_professional_id: UUID
    qualification_id: Optional[UUID] = None
    specialty_id: Optional[UUID] = None
    document_type: DocumentType
    document_category: DocumentCategory
    file_url: str
    file_name: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    expires_at: Optional[str] = None
    notes: Optional[str] = None

    # Verification
    is_verified: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
