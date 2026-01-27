"""ScreeningProcessStep model - individual step progress."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import JSON, Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import (
    ClientValidationOutcome,
    ConversationOutcome,
    StepStatus,
    StepType,
)
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    MetadataMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionMixin,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_document_review import (
        ScreeningDocumentReview,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class ScreeningProcessStepBase(BaseModel):
    """Base fields for ScreeningProcessStep."""

    step_type: StepType = Field(
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
        description="Type of screening step",
    )
    order: int = Field(
        ge=1,
        description="Order in which the step appears (from template)",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this step is mandatory (from template)",
    )
    status: StepStatus = Field(
        default=StepStatus.PENDING,
        sa_type=SAEnum(StepStatus, name="step_status", create_constraint=True),
        description="Current status of this step",
    )

    # Assignment
    assigned_to: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User responsible for this step",
    )

    # Data references (IDs of entities created/updated during this step)
    data_references: Optional[dict] = Field(
        default=None,
        sa_type=JSON,
        sa_column_kwargs={"nullable": True},
        description="References to data entities created/updated in this step (JSON)",
    )

    # Conversation step fields
    conversation_notes: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Notes from the conversation (for CONVERSATION step)",
    )
    conversation_outcome: Optional[ConversationOutcome] = Field(
        default=None,
        sa_type=SAEnum(
            ConversationOutcome, name="conversation_outcome", create_constraint=True
        ),
        description="Outcome of conversation: PROCEED or REJECT",
    )

    # Review fields
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the review",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Reason for rejection (if rejected)",
    )

    # Client validation step fields (for CLIENT_VALIDATION step)
    client_validation_outcome: Optional[ClientValidationOutcome] = Field(
        default=None,
        sa_type=SAEnum(
            ClientValidationOutcome,
            name="client_validation_outcome",
            create_constraint=True,
        ),
        description="Client's decision: APPROVED or REJECTED",
    )
    client_validation_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the client company validation",
    )
    client_validated_by: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Name of the person at client company who validated",
    )
    client_validated_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the client validation was performed",
    )


class ScreeningProcessStep(
    ScreeningProcessStepBase,
    MetadataMixin,
    VersionMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ScreeningProcessStep table model.

    Tracks progress of an individual step within a screening process.
    Created when screening process is initialized (one per template step).

    Data references store the IDs of entities created during the step:
    - PROFESSIONAL_DATA: {"professional_id": "uuid"}
    - QUALIFICATION: {"qualification_id": "uuid"}
    - SPECIALTY: {"specialty_ids": ["uuid1", "uuid2"]}
    - EDUCATION: {"education_ids": ["uuid1", "uuid2"]}
    - DOCUMENTS: {"document_ids": ["uuid1", "uuid2"]}
    - COMPANY: {"company_id": "uuid", "professional_company_id": "uuid"}
    - BANK_ACCOUNT: {"bank_account_id": "uuid"}

    For CONVERSATION step:
    - conversation_notes: Detailed notes from the phone call
    - conversation_outcome: PROCEED or REJECT

    Workflow timestamps:
    - started_at: When user started filling this step
    - submitted_at: When user completed this step
    - reviewed_at: When internal user reviewed this step
    """

    __tablename__ = "screening_process_steps"
    __table_args__ = (
        # Each step_type can only appear once per process
        UniqueConstraint(
            "process_id",
            "step_type",
            name="uq_screening_process_steps_process_step_type",
        ),
        # Index for listing steps by process
        Index("ix_screening_process_steps_process_id", "process_id"),
        # Index for filtering by status
        Index("ix_screening_process_steps_status", "status"),
        # Index for filtering by assigned user
        Index("ix_screening_process_steps_assigned_to", "assigned_to"),
    )

    # Process reference
    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
        description="Screening process this step belongs to",
    )

    # Workflow timestamps
    started_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this step was started",
    )
    submitted_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this step was submitted",
    )
    submitted_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who submitted this step (professional or internal user)",
    )
    reviewed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this step was reviewed",
    )
    reviewed_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who reviewed this step",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="steps")
    document_reviews: list["ScreeningDocumentReview"] = Relationship(
        back_populates="process_step",
    )

    @property
    def is_completed(self) -> bool:
        """Check if step is completed (submitted, approved, or skipped)."""
        return self.status in (
            StepStatus.COMPLETED,
            StepStatus.APPROVED,
            StepStatus.SKIPPED,
        )

    @property
    def can_be_started(self) -> bool:
        """Check if step can be started."""
        return self.status == StepStatus.PENDING

    @property
    def needs_correction(self) -> bool:
        """Check if step was rejected and needs correction."""
        return self.status in (StepStatus.REJECTED, StepStatus.CORRECTION_NEEDED)

    @property
    def is_conversation(self) -> bool:
        """Check if this is a conversation step."""
        return self.step_type == StepType.CONVERSATION

    @property
    def is_review_step(self) -> bool:
        """Check if this is a review step (DOCUMENT_REVIEW or SUPERVISOR_REVIEW)."""
        return self.step_type in (StepType.DOCUMENT_REVIEW, StepType.SUPERVISOR_REVIEW)
