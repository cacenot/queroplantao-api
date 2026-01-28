"""Base mixin for all screening step models."""

from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from src.modules.screening.domain.models.enums import StepStatus
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    VersionMixin,
)


class ScreeningStepBase(SQLModel):
    """
    Base fields shared by all screening steps.

    Contains common fields for workflow management that are present
    in every step type.
    """

    order: int = Field(
        ge=1,
        description="Order in which the step appears in the workflow",
    )
    status: StepStatus = Field(
        default=StepStatus.PENDING,
        sa_type=SAEnum(StepStatus, name="step_status", create_constraint=True),
        description="Current status of this step",
    )

    # Assignment (no FK - follows TrackingMixin pattern)
    assigned_to: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User responsible for this step",
    )

    # Review fields (applicable to steps that can be reviewed)
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


class ScreeningStepMixin(
    ScreeningStepBase, VersionMixin, PrimaryKeyMixin, TimestampMixin
):
    """
    Mixin with common fields for all step tables.

    Each concrete step table should inherit from this and add step-specific fields.
    Includes workflow timestamps for tracking step progression.

    Note: User ID fields (assigned_to, completed_by, reviewed_by) do NOT use FKs
    to avoid circular dependencies and allow soft-delete of users.
    """

    # Workflow timestamps
    started_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this step was started",
    )
    completed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this step was completed/submitted",
    )
    completed_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who completed this step (professional or internal user)",
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

    # === Properties ===

    @property
    def is_completed(self) -> bool:
        """Check if step is completed (submitted, approved, or skipped)."""
        return self.status in (
            StepStatus.COMPLETED,
            StepStatus.APPROVED,
            StepStatus.SKIPPED,
        )

    @property
    def is_approved(self) -> bool:
        """Check if step is approved."""
        return self.status == StepStatus.APPROVED

    @property
    def can_be_started(self) -> bool:
        """Check if step can be started."""
        return self.status == StepStatus.PENDING

    @property
    def is_in_progress(self) -> bool:
        """Check if step is in progress."""
        return self.status == StepStatus.IN_PROGRESS

    @property
    def needs_correction(self) -> bool:
        """Check if step was rejected and needs correction."""
        return self.status in (StepStatus.REJECTED, StepStatus.CORRECTION_NEEDED)

    @property
    def is_skipped(self) -> bool:
        """Check if step was skipped."""
        return self.status == StepStatus.SKIPPED
