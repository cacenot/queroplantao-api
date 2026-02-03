"""Document upload step schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from src.modules.screening.domain.schemas.steps.base import StepResponseBase


class DocumentConfigItem(BaseModel):
    """Single document configuration for the upload step."""

    model_config = ConfigDict(from_attributes=True)

    document_type_id: UUID = Field(
        description="ID of the document type to require",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this document is mandatory",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Display order (0 = first)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom instructions for uploading this document",
    )


class ConfigureDocumentsRequest(BaseModel):
    """Request schema for configuring documents in the upload step."""

    model_config = ConfigDict(from_attributes=True)

    documents: list[DocumentConfigItem] = Field(
        min_length=1,
        description="List of documents to configure for upload",
    )


class UploadDocumentFormData(BaseModel):
    """Form data for uploading a document.

    This is used for validation of Form() parameters.
    The actual file is received via UploadFile.

    The backend:
    1. Uploads the file to Firebase Storage
    2. Creates a ProfessionalDocument with is_pending=True
    3. Links it to the ScreeningDocument
    4. Updates status to PENDING_REVIEW

    The backend automatically infers:
    - qualification_id: from professional's primary qualification (for QUALIFICATION/SPECIALTY docs)
    - specialty_id: from screening's expected_specialty_id (for SPECIALTY docs)
    """

    model_config = ConfigDict(from_attributes=True)

    expires_at: Optional[AwareDatetime] = Field(
        default=None,
        description="Expiration date for documents with validity (UTC)",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Additional notes about this document",
    )


class DocumentUploadStepCompleteRequest(BaseModel):
    """Request schema for completing document upload step.

    This step is completed when all required documents have been uploaded.
    The system validates that all required documents have status != PENDING_UPLOAD.
    """

    model_config = ConfigDict(from_attributes=True)

    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional notes about the uploaded documents",
    )


class ScreeningDocumentSummary(BaseModel):
    """Summary of a document in the upload step response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type_id: UUID
    document_type_name: Optional[str] = None
    is_required: bool
    order: int
    status: str
    is_uploaded: bool
    uploaded_at: Optional[datetime] = None


class DocumentUploadStepResponse(StepResponseBase):
    """
    Response schema for document upload step.

    Includes document counts and optional document list.
    """

    # Configuration flag
    is_configured: bool = False

    # Document counts (denormalized)
    total_documents: int = 0
    required_documents: int = 0
    uploaded_documents: int = 0

    # Progress
    upload_progress: float = 0.0
    all_required_uploaded: bool = False

    # Optional: list of documents (for detailed view)
    documents: list[ScreeningDocumentSummary] = Field(default_factory=list)
