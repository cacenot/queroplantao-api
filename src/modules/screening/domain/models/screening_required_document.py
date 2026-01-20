"""ScreeningRequiredDocument model - documents required for a screening process."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import DocumentCategory, DocumentType
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_document_review import (
        ScreeningDocumentReview,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class ScreeningRequiredDocumentBase(BaseModel):
    """Base fields for ScreeningRequiredDocument."""

    document_type: DocumentType = Field(
        sa_type=SAEnum(DocumentType, name="document_type", create_constraint=True),
        description="Type of document required",
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


class ScreeningRequiredDocument(
    ScreeningRequiredDocumentBase,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ScreeningRequiredDocument table model.

    Defines which documents are required for a specific screening process.
    Configured when the screening is created, allowing customization per process.

    This allows the escalista to select which documents are mandatory for each
    screening, rather than having a fixed list in the template.

    Example document requirements for a medical professional:
    - Profile: ID_DOCUMENT (required), ADDRESS_PROOF (required), CRIMINAL_RECORD (required)
    - Qualification: DIPLOMA (required), CRM certificates (required)
    - Specialty: RESIDENCY_CERTIFICATE (optional), SPECIALIST_TITLE (optional)
    """

    __tablename__ = "screening_required_documents"
    __table_args__ = (
        # Each document type can only appear once per process
        UniqueConstraint(
            "process_id",
            "document_type",
            name="uq_screening_required_documents_process_doc_type",
        ),
        # Index for listing documents by process
        Index("ix_screening_required_documents_process_id", "process_id"),
        # Index for filtering by category
        Index("ix_screening_required_documents_category", "document_category"),
    )

    # Process reference
    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
        description="Screening process this document requirement belongs to",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="required_documents")
    reviews: list["ScreeningDocumentReview"] = Relationship(
        back_populates="required_document",
    )
