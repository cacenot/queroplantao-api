"""OrganizationScreeningSettings model - per-organization screening configuration."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
    VersionMixin,
)

if TYPE_CHECKING:
    from src.modules.organizations.domain.models.organization import Organization


class OrganizationScreeningSettingsBase(BaseModel):
    """Base fields for OrganizationScreeningSettings."""

    # Client company settings
    requires_client_company: bool = Field(
        default=False,
        description="Whether screenings require a client company (empresa contratante)",
    )
    requires_client_validation_step: bool = Field(
        default=False,
        description="Whether client validation step is required when client company is set",
    )

    # Document review settings
    auto_approve_existing_documents: bool = Field(
        default=False,
        description="Whether to auto-approve documents from previous screenings",
    )
    document_validity_check: bool = Field(
        default=True,
        description="Whether to check document expiration dates",
    )

    # Escalation settings
    escalation_enabled: bool = Field(
        default=True,
        description="Whether escalation to supervisor is enabled",
    )
    auto_escalate_alerts: bool = Field(
        default=False,
        description="Whether to auto-escalate when documents have alerts",
    )

    # Token/access settings
    token_expiry_hours: int = Field(
        default=72,
        ge=1,
        le=720,
        description="Hours until access token expires (1-720, default 72)",
    )
    allow_professional_self_service: bool = Field(
        default=True,
        description="Whether professionals can access screening via token link",
    )

    # Notifications
    notify_on_submission: bool = Field(
        default=True,
        description="Whether to notify assigned users when screening is submitted",
    )
    notify_on_expiration: bool = Field(
        default=True,
        description="Whether to notify when screening is about to expire",
    )


class OrganizationScreeningSettings(
    OrganizationScreeningSettingsBase,
    VersionMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    OrganizationScreeningSettings table model.

    Per-organization configuration for the screening process.
    Each organization has exactly one settings record (1:1 relationship).

    This allows organizations to customize their screening workflow:
    - Terceirizadoras: requires_client_company=True, requires_client_validation_step=True
    - Hospitais: requires_client_company=False, requires_client_validation_step=False

    Settings are created automatically when an organization is created,
    with sensible defaults that can be customized later.
    """

    __tablename__ = "organization_screening_settings"
    __table_args__ = (
        # 1:1 relationship with organization
        UniqueConstraint(
            "organization_id",
            name="uq_organization_screening_settings_org_id",
        ),
    )

    # Organization reference (1:1)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization these settings belong to",
    )

    # Relationships
    organization: "Organization" = Relationship()
