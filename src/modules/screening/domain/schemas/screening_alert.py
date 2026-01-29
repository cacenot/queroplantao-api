"""Schemas for ScreeningAlert."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.modules.screening.domain.models.enums import AlertCategory
from src.modules.screening.domain.models.screening_alert import AlertNote


class ScreeningAlertCreate(BaseModel):
    """Schema for creating a screening alert."""

    reason: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed reason for the alert",
    )
    category: AlertCategory = Field(
        ...,
        description="Category of the alert",
    )


class ScreeningAlertResolve(BaseModel):
    """Schema for resolving an alert (no risk, process continues)."""

    resolution_notes: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Notes explaining the resolution",
    )


class ScreeningAlertReject(BaseModel):
    """Schema for rejecting via alert (risk confirmed, process rejected)."""

    rejection_notes: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Notes explaining the rejection",
    )


class ScreeningAlertAddNote(BaseModel):
    """Schema for adding a note to an alert."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Note content",
    )


class ScreeningAlertResponse(BaseModel):
    """Response schema for a screening alert."""

    id: UUID
    process_id: UUID

    reason: str
    category: AlertCategory
    notes: list[AlertNote]
    is_resolved: bool

    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None

    created_at: datetime
    created_by: UUID
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScreeningAlertListResponse(BaseModel):
    """Response with alerts list and counts."""

    alerts: list[ScreeningAlertResponse]
    total_count: int
    pending_count: int
