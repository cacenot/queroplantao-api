"""ProfessionalDocument model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import (
    DocumentCategory,
    DocumentType,
)
from src.shared.domain.models import (
    AwareDatetimeField,
    BaseModel,
    PrimaryKeyMixin,
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


class ProfessionalDocumentBase(BaseModel):
    """Base fields for ProfessionalDocument."""

    document_type: DocumentType = Field(
        sa_type=SAEnum(DocumentType, name="document_type", create_constraint=True),
        description="Type of document (ID_DOCUMENT, DIPLOMA, etc.)",
    )
    document_category: DocumentCategory = Field(
        sa_type=SAEnum(
            DocumentCategory, name="document_category", create_constraint=True
        ),
        description="Category: PROFILE, QUALIFICATION, or SPECIALTY",
    )

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
    professional: "OrganizationProfessional" = Relationship(back_populates="documents")
    qualification: Optional["ProfessionalQualification"] = Relationship(
        back_populates="documents"
    )
    specialty: Optional["ProfessionalSpecialty"] = Relationship(
        back_populates="documents"
    )
