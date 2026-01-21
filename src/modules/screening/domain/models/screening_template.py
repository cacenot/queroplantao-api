"""ScreeningTemplate model - configurable screening templates."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import ProfessionalType
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    MetadataMixin,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.organizations.domain.models.organization import Organization
    from src.modules.screening.domain.models.screening_process import ScreeningProcess
    from src.modules.screening.domain.models.screening_template_step import (
        ScreeningTemplateStep,
    )


class ScreeningTemplateBase(BaseModel):
    """Base fields for ScreeningTemplate."""

    name: str = Field(
        max_length=255,
        description="Template name for identification",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Template description explaining its purpose",
    )
    professional_type: Optional[ProfessionalType] = Field(
        default=None,
        sa_type=SAEnum(
            ProfessionalType,
            name="professional_type",
            create_constraint=True,
        ),
        description="Type of professional this template is for (optional filter)",
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is the default template for the organization",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this template is available for use",
    )
    default_expiration_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Default number of days until screening process expires",
    )


class ScreeningTemplate(
    ScreeningTemplateBase,
    MetadataMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    ScreeningTemplate table model.

    Defines a configurable template for screening processes.
    Each organization can have multiple templates for different use cases
    (e.g., full onboarding, quick verification, specific contract requirements).

    Templates define which steps are required/optional and their order.
    Only one template can be marked as default per organization.
    """

    __tablename__ = "screening_templates"
    __table_args__ = (
        # Unique name per organization (when not soft-deleted)
        Index(
            "uq_screening_templates_org_name",
            "organization_id",
            "name",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        # Only one default template per organization
        Index(
            "uq_screening_templates_org_default",
            "organization_id",
            unique=True,
            postgresql_where="is_default = true AND deleted_at IS NULL",
        ),
        # Index for listing templates by organization
        Index("ix_screening_templates_organization_id", "organization_id"),
        # Index for filtering by professional type
        Index("ix_screening_templates_professional_type", "professional_type"),
    )

    # Organization reference (required - tenant isolation)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization that owns this template",
    )

    # Relationships
    organization: "Organization" = Relationship()
    steps: list["ScreeningTemplateStep"] = Relationship(
        back_populates="template",
        sa_relationship_kwargs={"order_by": "ScreeningTemplateStep.order"},
    )
    processes: list["ScreeningProcess"] = Relationship(
        back_populates="template",
    )
