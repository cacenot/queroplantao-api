"""Schemas for ProfessionalQualification."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.professionals.domain.models import CouncilType, ProfessionalType
from src.shared.domain.value_objects import StateUF

if TYPE_CHECKING:
    from src.modules.professionals.domain.schemas.professional_document import (
        ProfessionalDocumentResponse,
    )
    from src.modules.professionals.domain.schemas.professional_education import (
        ProfessionalEducationResponse,
    )
    from src.modules.professionals.domain.schemas.professional_specialty import (
        ProfessionalSpecialtyDetailResponse,
    )


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
    council_state: StateUF = Field(
        description="State where the council registration is valid (2 chars, e.g., SP, RJ)",
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
    council_state: Optional[StateUF] = Field(
        default=None,
        description="State where the council registration is valid (2 chars, e.g., SP, RJ)",
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

    # Computed properties
    is_generalist: bool = Field(
        default=False,
        description="True if professional is a doctor with no specialties (clínico geral)",
    )

    # Verification
    is_verified: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProfessionalQualificationDetailResponse(BaseModel):
    """Schema for professional qualification with nested data."""

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

    # Nested data
    specialties: list["ProfessionalSpecialtyDetailResponse"] = []
    educations: list["ProfessionalEducationResponse"] = []
    documents: list["ProfessionalDocumentResponse"] = []

    # Computed properties
    is_generalist: bool = Field(
        default=False,
        description="True if professional is a doctor with no specialties (clínico geral)",
    )

    # Verification
    is_verified: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Deferred imports to avoid circular imports
from src.modules.professionals.domain.schemas.professional_document import (  # noqa: E402
    ProfessionalDocumentResponse,
)
from src.modules.professionals.domain.schemas.professional_education import (  # noqa: E402
    ProfessionalEducationResponse,
)
from src.modules.professionals.domain.schemas.professional_specialty import (  # noqa: E402
    ProfessionalSpecialtyDetailResponse,
)

ProfessionalQualificationDetailResponse.model_rebuild()
