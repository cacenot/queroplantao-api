"""ProfessionalDocument model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Index, text
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    AwareDatetimeField,
    BaseModel,
    DocumentCategory,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.modules.professionals.domain.models.professional_qualification import (
        ProfessionalQualification,
    )
    from src.modules.professionals.domain.models.professional_specialty import (
        ProfessionalSpecialty,
    )
    from src.shared.domain.models import DocumentType


class ProfessionalDocumentBase(BaseModel):
    """Base fields for ProfessionalDocument."""

    # File information
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
        description="File size in bytes",
    )
    mime_type: Optional[str] = Field(
        default=None,
        max_length=100,
        description="MIME type of the file (e.g., application/pdf)",
    )

    # Expiration (for documents with validity period)
    expires_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Expiration date for documents with validity (UTC)",
    )

    # Additional notes
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about this document",
    )


class ProfessionalDocument(
    ProfessionalDocumentBase,
    VerificationMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    ProfessionalDocument table model.

    Stores documents uploaded by or for professionals.
    Multiple versions of the same document type can exist - the valid one
    is determined by: most recent + verified + not expired.

    Documents are always linked to a professional_profile for easy listing,
    and optionally to a qualification or specialty for more specific context.
    """

    __tablename__ = "professional_documents"
    __table_args__ = (
        # GIN trigram index for file_name search
        Index(
            "idx_professional_documents_filename_trgm",
            text("f_unaccent(lower(file_name))"),
            postgresql_using="gin",
            postgresql_ops={"": "gin_trgm_ops"},
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # B-tree index for document_type_id filtering
        Index(
            "idx_professional_documents_type_id",
            "document_type_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # B-tree index for expires_at filtering (only where not null)
        Index(
            "idx_professional_documents_expires",
            "expires_at",
            postgresql_where=text("deleted_at IS NULL AND expires_at IS NOT NULL"),
        ),
    )

    # Document type reference
    document_type_id: UUID = Field(
        foreign_key="document_types.id",
        nullable=False,
        description="Reference to the document type configuration",
    )

    # Always linked to organization professional (required for listing all docs)
    organization_professional_id: UUID = Field(
        foreign_key="organization_professionals.id",
        nullable=False,
        description="Organization professional ID (always required)",
    )

    # Optional links for QUALIFICATION and SPECIALTY category documents
    qualification_id: Optional[UUID] = Field(
        default=None,
        foreign_key="professional_qualifications.id",
        nullable=True,
        description="Professional qualification ID (for QUALIFICATION category)",
    )
    specialty_id: Optional[UUID] = Field(
        default=None,
        foreign_key="professional_specialties.id",
        nullable=True,
        description="Professional specialty ID (for SPECIALTY category)",
    )

    # Relationships
    document_type: "DocumentType" = Relationship(
        back_populates="professional_documents",
    )
    professional: "OrganizationProfessional" = Relationship(back_populates="documents")
    qualification: Optional["ProfessionalQualification"] = Relationship(
        back_populates="documents"
    )
    specialty: Optional["ProfessionalSpecialty"] = Relationship(
        back_populates="documents"
    )
    # Note: screening_reviews relationship is defined on ScreeningDocumentReview to avoid circular imports

    # === Properties ===

    @property
    def document_category(self) -> DocumentCategory:
        """Get document category from the document type."""
        return self.document_type.category
