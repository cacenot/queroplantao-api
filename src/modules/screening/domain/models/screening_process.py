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
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
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
    from src.modules.screening.domain.models.steps.client_validation_step import (
        ClientValidationStep,
    )
    from src.modules.screening.domain.models.steps.conversation_step import (
        ConversationStep,
    )
    from src.modules.screening.domain.models.steps.document_review_step import (
        DocumentReviewStep,
    )
    from src.modules.screening.domain.models.steps.document_upload_step import (
        DocumentUploadStep,
    )
    from src.modules.screening.domain.models.steps.payment_info_step import (
        PaymentInfoStep,
    )
    from src.modules.screening.domain.models.steps.professional_data_step import (
        ProfessionalDataStep,
    )
    from src.modules.screening.domain.models.steps.supervisor_review_step import (
        SupervisorReviewStep,
    )
    from src.shared.domain.models.company import Company


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
    expires_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this screening process expires",
    )

    # Assignment (no FK - follows TrackingMixin pattern)
    owner_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User responsible for this screening (owner)",
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

    # Expected professional profile (set during conversation step)
    expected_professional_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Expected professional type (DOCTOR, NURSE, etc.)",
    )
    expected_specialty_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="Expected specialty ID (for doctors)",
    )

    # Current actor tracking for "my pending screenings" filter (no FK)
    current_actor_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User currently responsible for the next action (for filtering)",
    )


class ScreeningProcess(
    ScreeningProcessBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    ScreeningProcess table model.

    Represents an individual screening instance for a professional.
    Now with modular steps - only configured steps are created.

    Key behaviors:
    - If professional doesn't exist (by CPF in org), one is created automatically
    - Professional can access via secure token link (no auth required)
    - Internal users (gestores/escalistas) can also fill on behalf of professional
    - Can be linked to contracts for tracking which screening led to which contract
    - Steps are optional 1:1 relationships - only exist if configured for this screening

    Workflow timestamps:
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
        # Index for owner
        Index("ix_screening_processes_owner", "owner_id"),
        # Index for current actor (for "my pending screenings" filter)
        Index("ix_screening_processes_current_actor", "current_actor_id"),
        # Index for client company
        Index("ix_screening_processes_client_company", "client_company_id"),
    )

    # Organization reference (required - tenant isolation)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization that owns this screening process",
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

    # Client company (empresa contratante) - for outsourcing companies
    client_company_id: Optional[UUID] = Field(
        default=None,
        foreign_key="companies.id",
        nullable=True,
        description="Client company (empresa contratante) for outsourcing scenarios",
    )

    # Workflow timestamp
    completed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When screening was approved/finalized",
    )

    # === Relationships ===

    # Core entity relationships
    organization: "Organization" = Relationship()
    organization_professional: Optional["OrganizationProfessional"] = Relationship()
    professional_contract: Optional["ProfessionalContract"] = Relationship()
    client_contract: Optional["ClientContract"] = Relationship(
        back_populates="screening_processes",
    )
    client_company: Optional["Company"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ScreeningProcess.client_company_id]",
        },
    )

    # Step relationships (optional 1:1 - only exist if step is configured)
    # Order: CONVERSATION -> PROFESSIONAL_DATA -> DOCUMENT_UPLOAD -> DOCUMENT_REVIEW
    #        -> PAYMENT_INFO -> SUPERVISOR_REVIEW -> CLIENT_VALIDATION
    conversation_step: Optional["ConversationStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"uselist": False},
    )
    professional_data_step: Optional["ProfessionalDataStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"uselist": False},
    )
    document_upload_step: Optional["DocumentUploadStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"uselist": False},
    )
    document_review_step: Optional["DocumentReviewStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"uselist": False},
    )
    payment_info_step: Optional["PaymentInfoStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"uselist": False},
    )
    supervisor_review_step: Optional["SupervisorReviewStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"uselist": False},
    )
    client_validation_step: Optional["ClientValidationStep"] = Relationship(
        back_populates="process",
        sa_relationship_kwargs={"uselist": False},
    )

    # === Properties ===

    @property
    def active_steps(self) -> list:
        """
        Get list of steps that exist for this process, sorted by order.

        Only returns steps that were actually configured/created for this screening.
        Steps are returned in fixed order:
        1. CONVERSATION (required)
        2. PROFESSIONAL_DATA (required)
        3. DOCUMENT_UPLOAD (required)
        4. DOCUMENT_REVIEW (required)
        5. PAYMENT_INFO (optional)
        6. SUPERVISOR_REVIEW (optional)
        7. CLIENT_VALIDATION (optional)
        """
        steps = []
        if self.conversation_step:
            steps.append(self.conversation_step)
        if self.professional_data_step:
            steps.append(self.professional_data_step)
        if self.document_upload_step:
            steps.append(self.document_upload_step)
        if self.document_review_step:
            steps.append(self.document_review_step)
        if self.payment_info_step:
            steps.append(self.payment_info_step)
        if self.supervisor_review_step:
            steps.append(self.supervisor_review_step)
        if self.client_validation_step:
            steps.append(self.client_validation_step)
        return sorted(steps, key=lambda s: s.order)

    @property
    def step_types(self) -> list[StepType]:
        """Get list of step types configured for this process."""
        return [step.step_type for step in self.active_steps]

    @property
    def current_step(self):
        """
        Get the current active step (first non-completed step in order).

        Returns None if all steps are completed.
        """
        for step in self.active_steps:
            if not step.is_completed:
                return step
        return None

    @property
    def current_step_type(self) -> Optional[StepType]:
        """Get the type of the current active step."""
        step = self.current_step
        return step.step_type if step else None

    @property
    def step_count(self) -> int:
        """Get total number of configured steps."""
        return len(self.active_steps)

    @property
    def completed_step_count(self) -> int:
        """Get number of completed steps."""
        return sum(1 for step in self.active_steps if step.is_completed)

    @property
    def progress_percentage(self) -> float:
        """Get overall progress as percentage (0-100)."""
        if self.step_count == 0:
            return 100.0
        return (self.completed_step_count / self.step_count) * 100

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
            ScreeningStatus.IN_PROGRESS,
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
        return self.status == ScreeningStatus.IN_PROGRESS and not self.is_expired

    @property
    def all_steps_completed(self) -> bool:
        """Check if all configured steps are completed."""
        return all(step.is_completed for step in self.active_steps)
