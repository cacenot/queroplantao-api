"""Schemas for ProfessionalSpecialty."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.professionals.domain.models import ResidencyStatus


class ProfessionalSpecialtyCreate(BaseModel):
    """Schema for creating a professional specialty."""

    model_config = ConfigDict(from_attributes=True)

    specialty_id: UUID = Field(
        description="The specialty UUID",
    )
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary specialty",
    )
    rqe_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="RQE number (for doctors)",
    )
    rqe_state: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="State where RQE is registered",
    )
    residency_status: ResidencyStatus = Field(
        default=ResidencyStatus.COMPLETED,
        description="Current residency/training status",
    )
    residency_institution: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Institution where residency is being done",
    )
    residency_expected_completion: Optional[str] = Field(
        default=None,
        description="Expected residency completion date (YYYY-MM-DD)",
    )
    certificate_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to specialty certificate",
    )


class ProfessionalSpecialtyUpdate(BaseModel):
    """Schema for updating a professional specialty (PATCH - partial update)."""

    model_config = ConfigDict(from_attributes=True)

    is_primary: Optional[bool] = Field(
        default=None,
        description="Whether this is the primary specialty",
    )
    rqe_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="RQE number (for doctors)",
    )
    rqe_state: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="State where RQE is registered",
    )
    residency_status: Optional[ResidencyStatus] = Field(
        default=None,
        description="Current residency/training status",
    )
    residency_institution: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Institution where residency is being done",
    )
    residency_expected_completion: Optional[str] = Field(
        default=None,
        description="Expected residency completion date (YYYY-MM-DD)",
    )
    certificate_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to specialty certificate",
    )


class SpecialtyInfo(BaseModel):
    """Embedded specialty information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: Optional[str] = None


class ProfessionalSpecialtyResponse(BaseModel):
    """Schema for professional specialty response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    qualification_id: UUID
    specialty_id: UUID
    is_primary: bool
    rqe_number: Optional[str] = None
    rqe_state: Optional[str] = None
    residency_status: ResidencyStatus
    residency_institution: Optional[str] = None
    residency_expected_completion: Optional[str] = None
    certificate_url: Optional[str] = None

    # Embedded specialty info
    specialty: Optional[SpecialtyInfo] = None

    # Verification
    is_verified: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
