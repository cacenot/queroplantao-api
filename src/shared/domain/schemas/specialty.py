"""Schemas for Specialty - global reference data."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SpecialtyResponse(BaseModel):
    """Schema for specialty response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SpecialtyListResponse(BaseModel):
    """Schema for specialty list item (simplified)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
