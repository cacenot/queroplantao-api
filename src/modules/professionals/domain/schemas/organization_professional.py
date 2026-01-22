"""Schemas for OrganizationProfessional."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.modules.professionals.domain.models import Gender, MaritalStatus


class OrganizationProfessionalCreate(BaseModel):
    """Schema for creating an organization professional."""

    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(
        max_length=255,
        description="Professional's full name",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Professional's email address",
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Phone number (E.164 format)",
    )
    cpf: Optional[str] = Field(
        default=None,
        min_length=11,
        max_length=11,
        description="Brazilian CPF (11 digits, no formatting)",
    )
    birth_date: Optional[str] = Field(
        default=None,
        description="Date of birth (YYYY-MM-DD)",
    )
    nationality: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nationality",
    )
    gender: Optional[Gender] = Field(
        default=None,
        description="Gender",
    )
    marital_status: Optional[MaritalStatus] = Field(
        default=None,
        description="Marital status",
    )
    avatar_url: Optional[str] = Field(
        default=None,
        max_length=2048,
        description="Profile picture URL",
    )

    # Address fields (required)
    city: str = Field(max_length=100, description="City name")
    state_code: str = Field(max_length=2, description="State code (e.g., SP, RJ)")
    state_name: str = Field(max_length=50, description="State name")
    postal_code: str = Field(max_length=10, description="Postal code (CEP)")

    # Address fields (optional)
    street: Optional[str] = Field(default=None, max_length=255)
    street_number: Optional[str] = Field(default=None, max_length=20)
    complement: Optional[str] = Field(default=None, max_length=100)
    neighborhood: Optional[str] = Field(default=None, max_length=100)


class OrganizationProfessionalUpdate(BaseModel):
    """Schema for updating an organization professional (PATCH - partial update)."""

    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Professional's full name",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Professional's email address",
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Phone number (E.164 format)",
    )
    cpf: Optional[str] = Field(
        default=None,
        min_length=11,
        max_length=11,
        description="Brazilian CPF (11 digits, no formatting)",
    )
    birth_date: Optional[str] = Field(
        default=None,
        description="Date of birth (YYYY-MM-DD)",
    )
    nationality: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nationality",
    )
    gender: Optional[Gender] = Field(
        default=None,
        description="Gender",
    )
    marital_status: Optional[MaritalStatus] = Field(
        default=None,
        description="Marital status",
    )
    avatar_url: Optional[str] = Field(
        default=None,
        max_length=2048,
        description="Profile picture URL",
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether this professional is active",
    )

    # Address fields
    street: Optional[str] = Field(default=None, max_length=255)
    street_number: Optional[str] = Field(default=None, max_length=20)
    complement: Optional[str] = Field(default=None, max_length=100)
    neighborhood: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    state_code: Optional[str] = Field(default=None, max_length=2)
    state_name: Optional[str] = Field(default=None, max_length=50)
    postal_code: Optional[str] = Field(default=None, max_length=10)


class OrganizationProfessionalResponse(BaseModel):
    """Schema for organization professional response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    birth_date: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    avatar_url: Optional[str] = None
    is_active: bool

    # Address fields
    street: Optional[str] = None
    street_number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    postal_code: Optional[str] = None

    # Verification
    is_verified: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QualificationSummary(BaseModel):
    """Summary of the primary professional qualification."""

    model_config = ConfigDict(from_attributes=True)

    professional_type: str
    council_type: str
    council_number: str
    council_state: str


class SpecialtySummary(BaseModel):
    """Summary of a specialty for list responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class OrganizationProfessionalListItem(BaseModel):
    """Simplified schema for professional list responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    avatar_url: Optional[str] = None
    full_name: str
    city: Optional[str] = None
    state_code: Optional[str] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    # Primary qualification summary
    qualification: Optional[QualificationSummary] = None

    # List of specialties
    specialties: list[SpecialtySummary] = []
