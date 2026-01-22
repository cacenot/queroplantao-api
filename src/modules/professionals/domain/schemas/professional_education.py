"""Schemas for ProfessionalEducation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.professionals.domain.models import EducationLevel


class ProfessionalEducationCreate(BaseModel):
    """Schema for creating a professional education record."""

    model_config = ConfigDict(from_attributes=True)

    level: EducationLevel = Field(
        description="Education level (undergraduate, masters, etc.)",
    )
    course_name: str = Field(
        max_length=255,
        description="Name of the course/degree",
    )
    institution: str = Field(
        max_length=255,
        description="Educational institution name",
    )
    start_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Year started",
    )
    end_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Year completed (null if ongoing)",
    )
    is_completed: bool = Field(
        default=False,
        description="Whether the education is completed",
    )
    workload_hours: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total workload in hours (for courses)",
    )
    certificate_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to certificate/diploma",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes",
    )


class ProfessionalEducationUpdate(BaseModel):
    """Schema for updating a professional education record (PATCH - partial update)."""

    model_config = ConfigDict(from_attributes=True)

    level: Optional[EducationLevel] = Field(
        default=None,
        description="Education level",
    )
    course_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Name of the course/degree",
    )
    institution: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Educational institution name",
    )
    start_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Year started",
    )
    end_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Year completed",
    )
    is_completed: Optional[bool] = Field(
        default=None,
        description="Whether the education is completed",
    )
    workload_hours: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total workload in hours",
    )
    certificate_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to certificate/diploma",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes",
    )


class ProfessionalEducationResponse(BaseModel):
    """Schema for professional education response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    qualification_id: UUID
    level: EducationLevel
    course_name: str
    institution: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    is_completed: bool
    workload_hours: Optional[int] = None
    certificate_url: Optional[str] = None
    notes: Optional[str] = None

    # Verification
    is_verified: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
