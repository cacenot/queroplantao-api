"""DocumentType model - configurable document types with help text."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship

from src.modules.professionals.domain.models.enums import DocumentCategory
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_required_document import (
        ScreeningRequiredDocument,
    )


class DocumentTypeConfigBase(BaseModel):
    """Base fields for DocumentTypeConfig."""

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


class DocumentTypeConfig(
    DocumentTypeConfigBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    DocumentTypeConfig table model.

    Stores configurable document types with help text and validation instructions.
    Replaces the DocumentType enum to allow runtime configuration.

    This is a global table (not organization-scoped) to maintain consistency
    across the platform. Organizations can customize which documents they require
    per screening via ScreeningRequiredDocument.

    Example entries:
    - code: "CRM_REGISTRATION_CERTIFICATE"
      name: "Certidão de Regularidade de Inscrição"
      help_text: "Acesse o portal do CRM do seu estado e solicite a certidão..."
      validation_url: "https://portal.cfm.org.br"
    """

    __tablename__ = "document_type_configs"
    __table_args__ = (
        # Unique code (soft delete aware)
        UniqueConstraint(
            "code",
            name="uq_document_type_configs_code",
        ),
        Index(
            "ix_document_type_configs_code_active",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Index for category filtering
        Index("ix_document_type_configs_category", "category"),
        # Index for active documents
        Index("ix_document_type_configs_is_active", "is_active"),
    )

    # Organization scope (optional - null means global/system-defined)
    organization_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organizations.id",
        nullable=True,
        description="Organization that created this type (null = system-defined)",
    )

    # Relationships
    required_documents: list["ScreeningRequiredDocument"] = Relationship(
        back_populates="document_type_config",
    )
