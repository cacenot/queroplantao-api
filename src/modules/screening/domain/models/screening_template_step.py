"""ScreeningTemplateStep model - template step configuration."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import JSON, Enum as SAEnum, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import StepType
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    MetadataMixin,
    PrimaryKeyMixin,
    TimestampMixin,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_template import ScreeningTemplate


class ScreeningTemplateStepBase(BaseModel):
    """Base fields for ScreeningTemplateStep."""

    step_type: StepType = Field(
        sa_type=SAEnum(StepType, name="step_type", create_constraint=True),
        description="Type of screening step",
    )
    order: int = Field(
        ge=1,
        description="Order in which the step appears (1-based)",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this step is mandatory",
    )
    is_enabled: bool = Field(
        default=True,
        description="Whether this step is enabled in the template",
    )
    instructions: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Custom instructions for this step",
    )
    depends_on: Optional[list[str]] = Field(
        default=None,
        sa_type=JSON,
        sa_column_kwargs={"nullable": True},
        description="List of StepType values this step depends on (JSON array)",
    )


class ScreeningTemplateStep(
    ScreeningTemplateStepBase,
    MetadataMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ScreeningTemplateStep table model.

    Defines the configuration of a step within a screening template.
    Each template can have multiple steps with configurable order,
    requirements, and dependencies.

    Dependencies allow steps to be blocked until other steps are completed
    (e.g., SPECIALTY requires QUALIFICATION to be completed first).
    """

    __tablename__ = "screening_template_steps"
    __table_args__ = (
        # Each step_type can only appear once per template
        UniqueConstraint(
            "template_id",
            "step_type",
            name="uq_screening_template_steps_template_step_type",
        ),
        # Unique order per template
        UniqueConstraint(
            "template_id",
            "order",
            name="uq_screening_template_steps_template_order",
        ),
    )

    # Template reference
    template_id: UUID = Field(
        foreign_key="screening_templates.id",
        nullable=False,
        description="Template this step belongs to",
    )

    # Relationships
    template: "ScreeningTemplate" = Relationship(back_populates="steps")
