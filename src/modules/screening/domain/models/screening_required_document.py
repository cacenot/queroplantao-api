"""ScreeningRequiredDocument model - documents required for a screening process."""

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import DocumentCategory, DocumentType
from src.modules.screening.domain.models.enums import RequiredDocumentStatus
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_document import (
        ProfessionalDocument,
    )
    from src.modules.screening.domain.models.document_type import DocumentTypeConfig
    from src.modules.screening.domain.models.screening_document_review import (
        ScreeningDocumentReview,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class ScreeningRequiredDocumentBase(BaseModel):
    """Base fields for ScreeningRequiredDocument."""

    # Legacy enum field (kept for backward compatibility)
    document_type: Optional[DocumentType] = Field(
        default=None,
        sa_type=SAEnum(DocumentType, name="document_type", create_constraint=True),
        description="Type of document required (legacy enum)",
    )
    document_category: DocumentCategory = Field(
        sa_type=SAEnum(
            DocumentCategory, name="document_category", create_constraint=True
        ),
        description="Category of document (PROFILE, QUALIFICATION, SPECIALTY)",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this document is mandatory or optional",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom description or instructions for this document",
    )

    # Document status tracking
    status: RequiredDocumentStatus = Field(
        default=RequiredDocumentStatus.PENDING_UPLOAD,
        sa_type=SAEnum(
            RequiredDocumentStatus,
            name="required_document_status",
            create_constraint=True,
        ),
        description="Current status of this required document",
    )

    # Review notes history - JSONB array of {user_id, text, created_at, action}
    review_notes: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_type=JSONB,
        description="History of review notes for this document",
    )

    # Upload tracking (kept for backward compatibility, derived from status)
    is_uploaded: bool = Field(
        default=False,
        description="Whether document has been uploaded",
    )
    is_existing: bool = Field(
        default=False,
        description="Whether document was reused from previous screening",
    )


class ScreeningRequiredDocument(
    ScreeningRequiredDocumentBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ScreeningRequiredDocument table model.

    Defines which documents are required for a specific screening process.
    Configured when the screening is created (step 2), allowing customization per process.

    This allows the escalista to select which documents are mandatory for each
    screening, rather than having a fixed list in the template.

    Supports both:
    - Legacy enum-based document types (document_type field)
    - New configurable document types (document_type_config_id)

    Example document requirements for a medical professional:
    - Profile: ID_DOCUMENT (required), ADDRESS_PROOF (required), CRIMINAL_RECORD (required)
    - Qualification: DIPLOMA (required), CRM certificates (required)
    - Specialty: RESIDENCY_CERTIFICATE (optional), SPECIALIST_TITLE (optional)
    """

    __tablename__ = "screening_required_documents"
    __table_args__ = (
        # Each document type can only appear once per process (using config FK)
        UniqueConstraint(
            "process_id",
            "document_type_config_id",
            name="uq_screening_required_documents_process_doc_config",
        ),
        # Legacy constraint for enum-based types
        UniqueConstraint(
            "process_id",
            "document_type",
            name="uq_screening_required_documents_process_doc_type",
        ),
        # Index for listing documents by process
        Index("ix_screening_required_documents_process_id", "process_id"),
        # Index for filtering by category
        Index("ix_screening_required_documents_category", "document_category"),
        # Index for document type config
        Index(
            "ix_screening_required_documents_doc_type_config", "document_type_config_id"
        ),
    )

    # Process reference
    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
        description="Screening process this document requirement belongs to",
    )

    # Document type config reference (new system)
    document_type_config_id: Optional[UUID] = Field(
        default=None,
        foreign_key="document_type_configs.id",
        nullable=True,
        description="Reference to configurable document type",
    )

    # Professional document reference (if uploaded/reused)
    professional_document_id: Optional[UUID] = Field(
        default=None,
        foreign_key="professional_documents.id",
        nullable=True,
        description="The actual uploaded document for this requirement",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="required_documents")
    document_type_config: Optional["DocumentTypeConfig"] = Relationship(
        back_populates="required_documents",
    )
    professional_document: Optional["ProfessionalDocument"] = Relationship()
    reviews: list["ScreeningDocumentReview"] = Relationship(
        back_populates="required_document",
    )
