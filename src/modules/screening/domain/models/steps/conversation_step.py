"""Conversation step - initial phone screening."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import ConversationOutcome, StepType
from src.modules.screening.domain.models.steps.base_step import ScreeningStepMixin
from src.shared.domain.models.base import BaseModel

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class ConversationStepBase(BaseModel):
    """Conversation-specific fields."""

    notes: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Detailed notes from the phone call",
    )
    outcome: Optional[ConversationOutcome] = Field(
        default=None,
        sa_type=SAEnum(
            ConversationOutcome, name="conversation_outcome", create_constraint=True
        ),
        description="Outcome of conversation: PROCEED or REJECT",
    )


class ConversationStep(ConversationStepBase, ScreeningStepMixin, table=True):
    """
    Conversation step table.

    Initial phone screening before data collection.
    Used to assess if the professional is a good fit before collecting detailed data.

    Workflow:
    1. Escalista calls the professional
    2. Takes notes during conversation
    3. Sets outcome: PROCEED (continue screening) or REJECT (end here)
    """

    __tablename__ = "screening_conversation_steps"
    __table_args__ = (
        UniqueConstraint(
            "process_id",
            name="uq_screening_conversation_steps_process_id",
        ),
        Index("ix_screening_conversation_steps_process_id", "process_id"),
        Index("ix_screening_conversation_steps_status", "status"),
    )

    step_type: StepType = Field(
        default=StepType.CONVERSATION,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
        description="Always CONVERSATION for this table",
    )

    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
        description="Screening process this step belongs to",
    )

    # Relationship
    process: "ScreeningProcess" = Relationship(back_populates="conversation_step")

    @property
    def proceeded(self) -> bool:
        """Check if conversation resulted in proceeding."""
        return self.outcome == ConversationOutcome.PROCEED

    @property
    def rejected(self) -> bool:
        """Check if conversation resulted in rejection."""
        return self.outcome == ConversationOutcome.REJECT
