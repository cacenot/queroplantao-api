"""Schemas for ScreeningProcessStep."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.screening.domain.models.enums import (
    ClientValidationOutcome,
    ConversationOutcome,
    StepStatus,
    StepType,
)


class ScreeningProcessStepUpdate(BaseModel):
    """Schema for updating a screening process step (PATCH)."""

    model_config = ConfigDict(from_attributes=True)

    status: Optional[StepStatus] = None
    assigned_to: Optional[UUID] = None
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
    )


class ConversationStepData(BaseModel):
    """Schema for conversation step data (Step 1)."""

    model_config = ConfigDict(from_attributes=True)

    conversation_notes: str = Field(
        max_length=4000,
        description="Notes from the phone call",
    )
    conversation_outcome: ConversationOutcome = Field(
        description="Outcome: PROCEED or REJECT",
    )


class ClientValidationStepData(BaseModel):
    """Schema for client validation step data (Step 6)."""

    model_config = ConfigDict(from_attributes=True)

    client_validation_outcome: ClientValidationOutcome = Field(
        description="Client decision: APPROVED or REJECTED",
    )
    client_validation_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the client",
    )
    client_validated_by: str = Field(
        max_length=255,
        description="Name of person who validated",
    )


class ScreeningClientValidationComplete(BaseModel):
    """Schema for completing client validation step."""

    model_config = ConfigDict(from_attributes=True)

    outcome: ClientValidationOutcome = Field(
        description="Client validation outcome",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Client notes",
    )
    validated_by_name: str = Field(
        max_length=255,
        description="Name of person at client who validated",
    )


class ScreeningProcessStepAdvance(BaseModel):
    """Schema for advancing a step."""

    model_config = ConfigDict(from_attributes=True)

    # Optional step-specific data
    conversation_data: Optional[ConversationStepData] = None
    client_validation_data: Optional[ClientValidationStepData] = None

    # Generic notes
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
    )


class StepSummaryResponse(BaseModel):
    """
    Minimal schema for step summary in process detail.

    Used to show a list of steps without full details.
    Ordered by 'order' field.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    step_type: StepType
    order: int
    status: StepStatus
    is_current: bool = Field(
        default=False,
        description="Whether this is the current active step",
    )


class ScreeningProcessStepResponse(BaseModel):
    """Schema for screening process step response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    process_id: UUID
    step_type: StepType
    order: int
    is_required: bool
    status: StepStatus
    assigned_to: Optional[UUID]

    # Data references
    data_references: Optional[dict[str, Any]]

    # Conversation fields
    conversation_notes: Optional[str]
    conversation_outcome: Optional[ConversationOutcome]

    # Review fields
    review_notes: Optional[str]
    rejection_reason: Optional[str]

    # Client validation fields
    client_validation_outcome: Optional[ClientValidationOutcome]
    client_validation_notes: Optional[str]
    client_validated_by: Optional[str]
    client_validated_at: Optional[datetime]

    # Timestamps
    started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    submitted_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
