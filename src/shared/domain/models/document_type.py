"""DocumentType model - configurable document types with help text."""

from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index, Text, UniqueConstraint, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_document import (
        ProfessionalDocument,
    )
    from src.modules.screening.domain.models.screening_document import (
        ScreeningDocument,
    )


class DocumentCategory(str, Enum):
    """
    Document category based on which entity it relates to.

    Used to group documents by their relation to professional data.
    """

    PROFILE = "PROFILE"  # Documentos pessoais do profissional
    QUALIFICATION = "QUALIFICATION"  # Documentos da qualificação/conselho
    SPECIALTY = "SPECIALTY"  # Documentos da especialidade


class DocumentTypeBase(BaseModel):
    """Base fields for DocumentType."""

    # Identification
    code: str = Field(
        max_length=50,
        description="Unique code for this document type (e.g., 'ID_DOCUMENT', 'CRM_CERTIFICATE')",
    )
    name: str = Field(
        max_length=255,
        description="Display name in Portuguese (e.g., 'Documento de Identidade')",
    )
    category: DocumentCategory = Field(
        sa_type=SAEnum(
            DocumentCategory, name="document_category", create_constraint=True
        ),
        description="Document category (PROFILE, QUALIFICATION, SPECIALTY)",
    )

    # Help information
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Brief description of this document",
    )
    help_text: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="Detailed help text on how to obtain this document",
    )
    validation_instructions: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="Instructions for reviewers on how to validate this document",
    )
    validation_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL where this document can be validated (e.g., CRM website)",
    )

    # Configuration
    requires_expiration: bool = Field(
        default=False,
        description="Whether this document type has an expiration date",
    )
    default_validity_days: Optional[int] = Field(
        default=None,
        description="Default validity period in days (e.g., 90 for criminal record)",
    )

    # Professional type requirements
    required_for_professional_types: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="List of ProfessionalType values this doc is required for (null = all)",
    )

    # Status
    is_active: bool = Field(
        default=True,
        description="Whether this document type is currently in use",
    )

    # Display
    display_order: int = Field(
        default=0,
        description="Order for displaying in lists (lower = first)",
    )


class DocumentType(
    DocumentTypeBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    DocumentType table model.

    Stores configurable document types with help text and validation instructions.
    This is a global table with optional organization-specific customizations.

    Document types can be:
    - Global (organization_id=None): Available to all organizations, system-defined
    - Organization-specific: Custom types created by an organization

    Example entries:
    - code: "CRM_REGISTRATION_CERTIFICATE"
      name: "Certidão de Regularidade de Inscrição"
      help_text: "Acesse o portal do CRM do seu estado e solicite a certidão..."
      validation_url: "https://portal.cfm.org.br"
    """

    __tablename__ = "document_types"
    __table_args__ = (
        # Unique code per organization (null org = global)
        UniqueConstraint(
            "code",
            "organization_id",
            name="uq_document_types_code_org",
        ),
        # Unique index for active global types
        Index(
            "ix_document_types_code_global_active",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND organization_id IS NULL"),
        ),
        # Index for category filtering
        Index("ix_document_types_category", "category"),
        # Index for active documents
        Index("ix_document_types_is_active", "is_active"),
        # Index for organization filtering
        Index("ix_document_types_organization_id", "organization_id"),
    )

    # Organization scope (optional - null means global/system-defined)
    organization_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organizations.id",
        nullable=True,
        description="Organization that created this type (null = system-defined)",
    )

    # Relationships
    professional_documents: list["ProfessionalDocument"] = Relationship(
        back_populates="document_type",
    )
    screening_documents: list["ScreeningDocument"] = Relationship(
        back_populates="document_type",
    )
