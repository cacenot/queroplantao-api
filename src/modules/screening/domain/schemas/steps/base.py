"""Base schema for step responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.modules.screening.domain.models.enums import StepStatus, StepType


class StepResponseBase(BaseModel):
    """
    Base schema with common fields for all step responses.

    All step response schemas should inherit from this.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    step_type: StepType
    order: int
    status: StepStatus

    # Assignment
    assigned_to: Optional[UUID] = None

    # Review fields
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[UUID] = None
