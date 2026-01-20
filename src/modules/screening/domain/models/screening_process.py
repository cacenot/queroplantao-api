"""ScreeningProcess model - individual screening instances."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum, Index
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import ScreeningStatus, StepType
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField, CPFField, PhoneField
from src.shared.domain.models.mixins import (
    MetadataMixin,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
    VersionMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.client_contract import ClientContract
    from src.modules.contracts.domain.models.professional_contract import (
        ProfessionalContract,
    )
    from src.modules.organizations.domain.models.organization import Organization
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.modules.screening.domain.models.screening_document_review import (
        ScreeningDocumentReview,
    )
    from src.modules.screening.domain.models.screening_process_step import (
        ScreeningProcessStep,
    )
    from src.modules.screening.domain.models.screening_required_document import (
        ScreeningRequiredDocument,
    )
    from src.modules.screening.domain.models.screening_template import ScreeningTemplate


class ScreeningProcessBase(BaseModel):
    """Base fields for ScreeningProcess."""

    status: ScreeningStatus = Field(
        default=ScreeningStatus.DRAFT,
        sa_type=SAEnum(
            ScreeningStatus, name="screening_status", create_constraint=True
        ),
        description="Current status of the screening process",
    )

    # Professional identification (used for lookup/creation)
    professional_cpf: Optional[str] = CPFField(
        default=None,
        nullable=True,
        description="Professional's CPF (used to find or create professional record)",
    )
    professional_email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Professional's email for sending screening link",
    )
    professional_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Professional's name (for display before record exists)",
    )
    professional_phone: Optional[str] = PhoneField(
        default=None,
        nullable=True,
        description="Professional's phone number (E.164 format)",
    )

    # Access token for professional self-service
    access_token: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Secure token for professional to access screening (SHA-256 hash)",
    )
    access_token_expires_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the access token expires",
    )

    # Process management
    current_step_type: Optional[StepType] = Field(
        default=None,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
        description="Current active step type",
    )
    expires_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this screening process expires",
    )

    # Assignment
    assigned_to: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User currently responsible for this screening",
    )
    escalated_to: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="Supervisor assigned for escalated review",
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Reason for escalation to supervisor",
    )

    # Rejection
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Reason for rejection (if rejected)",
    )

    # Notes
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Internal notes about this screening",
    )


class ScreeningProcess(
    ScreeningProcessBase,
    MetadataMixin,
    VersionMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    ScreeningProcess table model.

    Represents an individual screening instance for a professional.
    Tracks progress through the configured steps from the template.

    Key behaviors:
    - If professional doesn't exist (by CPF in org), one is created automatically
    - Professional can access via secure token link (no auth required)
    - Internal users (gestores/escalistas) can also fill on behalf of professional
    - Can be linked to contracts for tracking which screening led to which contract

    Workflow timestamps track progress:
    - sent_at: When screening link was sent to professional
    - started_at: When professional/user first accessed the screening
    - submitted_at: When all required steps were completed
    - reviewed_at: When internal user reviewed the submission
    - completed_at: When screening was approved/finalized
    """

    __tablename__ = "screening_processes"
    __table_args__ = (
        # Index for listing by organization
        Index("ix_screening_processes_organization_id", "organization_id"),
        # Index for filtering by status
        Index("ix_screening_processes_status", "status"),
        # Index for filtering by professional
        Index("ix_screening_processes_professional_id", "organization_professional_id"),
        # Index for token-based access
        Index(
            "ix_screening_processes_access_token",
            "access_token",
            unique=True,
            postgresql_where="access_token IS NOT NULL",
        ),
        # Unique active screening per professional per organization
        Index(
            "uq_screening_processes_org_cpf_active",
            "organization_id",
            "professional_cpf",
            unique=True,
            postgresql_where=(
                "status NOT IN ('APPROVED', 'REJECTED', 'EXPIRED', 'CANCELLED') "
                "AND deleted_at IS NULL AND professional_cpf IS NOT NULL"
            ),
        ),
        # Index for assigned user
        Index("ix_screening_processes_assigned_to", "assigned_to"),
        # Index for escalated processes
        Index("ix_screening_processes_escalated_to", "escalated_to"),
    )

    # Organization reference (required - tenant isolation)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization that owns this screening process",
    )

    # Template used (required)
    template_id: UUID = Field(
        foreign_key="screening_templates.id",
        nullable=False,
        description="Template defining the steps for this screening",
    )

    # Professional reference (created during screening if doesn't exist)
    organization_professional_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organization_professionals.id",
        nullable=True,
        description="Professional being screened (linked when found/created)",
    )

    # Optional contract bindings
    professional_contract_id: Optional[UUID] = Field(
        default=None,
        foreign_key="professional_contracts.id",
        nullable=True,
        description="Professional contract this screening is for (if applicable)",
    )
    client_contract_id: Optional[UUID] = Field(
        default=None,
        foreign_key="client_contracts.id",
        nullable=True,
        description="Client contract this screening is for (if applicable)",
    )

    # Workflow timestamps
    sent_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When screening link was sent to professional",
    )
    started_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When screening was first accessed",
    )
    submitted_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When all required steps were completed",
    )
    reviewed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When internal user reviewed the submission",
    )
    reviewed_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who reviewed the screening",
    )
    completed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When screening was approved/finalized",
    )

    # Review notes (for rejection reason, etc.)
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the review (e.g., rejection reason)",
    )

    # Relationships
    organization: "Organization" = Relationship(
        back_populates="screening_processes",
    )
    template: "ScreeningTemplate" = Relationship(
        back_populates="processes",
    )
    organization_professional: Optional["OrganizationProfessional"] = Relationship(
        back_populates="screening_processes",
    )
    professional_contract: Optional["ProfessionalContract"] = Relationship(
        back_populates="screening_processes",
    )
    client_contract: Optional["ClientContract"] = Relationship(
        back_populates="screening_processes",
    )
    steps: list["ScreeningProcessStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"order_by": "ScreeningProcessStep.order"},
    )
    required_documents: list["ScreeningRequiredDocument"] = Relationship(
        back_populates="process",
    )
    document_reviews: list["ScreeningDocumentReview"] = Relationship(
        back_populates="process",
    )

    @property
    def is_expired(self) -> bool:
        """Check if screening has expired."""
        from datetime import datetime, timezone

        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_active(self) -> bool:
        """Check if screening is in an active state."""
        return self.status in (
            ScreeningStatus.DRAFT,
            ScreeningStatus.CONVERSATION,
            ScreeningStatus.IN_PROGRESS,
            ScreeningStatus.PENDING_REVIEW,
            ScreeningStatus.UNDER_REVIEW,
            ScreeningStatus.PENDING_CORRECTION,
            ScreeningStatus.ESCALATED,
        )

    @property
    def is_terminal(self) -> bool:
        """Check if screening is in a terminal (final) state."""
        return self.status in (
            ScreeningStatus.APPROVED,
            ScreeningStatus.REJECTED,
            ScreeningStatus.EXPIRED,
            ScreeningStatus.CANCELLED,
        )

    @property
    def can_be_filled(self) -> bool:
        """Check if screening can still accept input."""
        return self.status in (
            ScreeningStatus.CONVERSATION,
            ScreeningStatus.IN_PROGRESS,
            ScreeningStatus.PENDING_CORRECTION,
        ) and not self.is_expired
