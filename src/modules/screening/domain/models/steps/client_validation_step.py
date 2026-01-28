"""Client validation step - approval by client company."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import ClientValidationOutcome, StepType
from src.modules.screening.domain.models.steps.base_step import ScreeningStepMixin
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class ClientValidationStepBase(BaseModel):
    """Client validation-specific fields."""

    outcome: Optional[ClientValidationOutcome] = Field(
        default=None,
        sa_type=SAEnum(
            ClientValidationOutcome,
            name="client_validation_outcome",
            create_constraint=True,
        ),
        description="Client's decision: APPROVED or REJECTED",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the client company validation",
    )
    validated_by: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Name of the person at client company who validated",
    )
    validated_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the client validation was performed",
    )


class ClientValidationStep(ClientValidationStepBase, ScreeningStepMixin, table=True):
    """
    Client validation step table.

    Client company approves or rejects the professional.
    This is the final step for screenings that require client approval.

    Workflow:
    1. Internal user sends professional data to client company
    2. Client reviews and makes decision
    3. Escalista records outcome, who validated, and when
    4. If APPROVED, screening completes. If REJECTED, screening is rejected.
    """

    __tablename__ = "screening_client_validation_steps"
    __table_args__ = (
        UniqueConstraint(
            "process_id",
            name="uq_screening_client_validation_steps_process_id",
        ),
        Index("ix_screening_client_validation_steps_process_id", "process_id"),
        Index("ix_screening_client_validation_steps_status", "status"),
    )

    step_type: StepType = Field(
        default=StepType.CLIENT_VALIDATION,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
    )

    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
    )

    process: "ScreeningProcess" = Relationship(back_populates="client_validation_step")

    @property
    def client_approved(self) -> bool:
        """Check if client approved."""
        return self.outcome == ClientValidationOutcome.APPROVED

    @property
    def client_rejected(self) -> bool:
        """Check if client rejected."""
        return self.outcome == ClientValidationOutcome.REJECTED

    @property
    def has_outcome(self) -> bool:
        """Check if outcome has been set."""
        return self.outcome is not None
