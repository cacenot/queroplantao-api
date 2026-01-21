"""Schemas for ProfessionalQualification."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.professionals.domain.models import CouncilType, ProfessionalType


class ProfessionalQualificationCreate(BaseModel):
    """Schema for creating a professional qualification."""

    model_config = ConfigDict(from_attributes=True)

    professional_type: ProfessionalType = Field(
        description="Type of healthcare professional (DOCTOR, NURSE, etc.)",
    )
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary qualification",
    )
    graduation_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Year of graduation",
    )
    council_type: CouncilType = Field(
        description="Council type (CRM, COREN, etc.)",
    )
    council_number: str = Field(
        max_length=20,
        description="Council registration number",
    )
    council_state: str = Field(
        min_length=2,
        max_length=2,
        description="State where the council registration is valid (2 chars)",
    )


class ProfessionalQualificationUpdate(BaseModel):
    """Schema for updating a professional qualification (PATCH - partial update)."""

    model_config = ConfigDict(from_attributes=True)

    is_primary: Optional[bool] = Field(
        default=None,
        description="Whether this is the primary qualification",
    )
    graduation_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Year of graduation",
    )
    council_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Council registration number",
    )
    council_state: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="State where the council registration is valid",
    )


class ProfessionalQualificationResponse(BaseModel):
    """Schema for professional qualification response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_professional_id: UUID
    organization_id: UUID
    professional_type: ProfessionalType
    is_primary: bool
    graduation_year: Optional[int] = None
    council_type: CouncilType
    council_number: str
    council_state: str

    # Verification
    is_verified: bool = False

    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
