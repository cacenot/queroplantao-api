"""Supervisor review step - escalated review for documents with alerts."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import StepType
from src.modules.screening.domain.models.steps.base_step import ScreeningStepMixin
from src.shared.domain.models.base import BaseModel

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class SupervisorReviewStepBase(BaseModel):
    """Supervisor review-specific fields."""

    escalation_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Reason why this was escalated to supervisor",
    )
    supervisor_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the supervisor review",
    )
    alert_document_count: int = Field(
        default=0,
        ge=0,
        description="Number of documents that triggered alerts",
    )


class SupervisorReviewStep(SupervisorReviewStepBase, ScreeningStepMixin, table=True):
    """
    Supervisor review step table.

    Escalated review for documents or data that require supervisor attention.
    Created when DocumentReviewStep has documents with ALERT status.

    Workflow:
    1. DocumentReviewStep completes with ALERT documents
    2. SupervisorReviewStep is created/activated
    3. Supervisor reviews flagged documents
    4. Makes final decision: APPROVED or REJECTED
    """

    __tablename__ = "screening_supervisor_review_steps"
    __table_args__ = (
        UniqueConstraint(
            "process_id",
            name="uq_screening_supervisor_review_steps_process_id",
        ),
        Index("ix_screening_supervisor_review_steps_process_id", "process_id"),
        Index("ix_screening_supervisor_review_steps_status", "status"),
    )

    step_type: StepType = Field(
        default=StepType.SUPERVISOR_REVIEW,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
    )

    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
    )

    process: "ScreeningProcess" = Relationship(back_populates="supervisor_review_step")

    @property
    def has_escalation_reason(self) -> bool:
        """Check if escalation reason was provided."""
        return self.escalation_reason is not None and len(self.escalation_reason) > 0
