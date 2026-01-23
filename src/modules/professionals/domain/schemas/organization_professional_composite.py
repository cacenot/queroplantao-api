"""Composite schemas for creating/updating professionals with nested entities."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from src.modules.professionals.domain.models import (
    CouncilType,
    EducationLevel,
    Gender,
    MaritalStatus,
    ProfessionalType,
    ResidencyStatus,
)
from src.shared.domain.value_objects import CPF, Phone, StateUF


# =============================================================================
# Specialty nested schemas (for composite create/update)
# =============================================================================


class SpecialtyNestedCreate(BaseModel):
    """Schema for creating a specialty within a composite operation."""

    model_config = ConfigDict(from_attributes=True)

    specialty_id: UUID = Field(
        description="The specialty UUID (must exist in global specialties table)",
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
    rqe_state: Optional[StateUF] = Field(
        default=None,
        description="State where RQE is registered (e.g., SP, RJ)",
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
    certificate_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL to specialty certificate",
    )


class SpecialtyNestedUpdate(BaseModel):
    """Schema for updating a specialty within a composite operation."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(
        default=None,
        description="Specialty ID (required for update, omit for create, send only ID to keep unchanged)",
    )
    specialty_id: Optional[UUID] = Field(
        default=None,
        description="The specialty UUID (required for create)",
    )
    is_primary: Optional[bool] = Field(
        default=None,
        description="Whether this is the primary specialty",
    )
    rqe_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="RQE number (for doctors)",
    )
    rqe_state: Optional[StateUF] = Field(
        default=None,
        description="State where RQE is registered (e.g., SP, RJ)",
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
    certificate_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL to specialty certificate",
    )


# =============================================================================
# Education nested schemas (for composite create/update)
# =============================================================================


class EducationNestedCreate(BaseModel):
    """Schema for creating an education within a composite operation."""

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
    certificate_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL to certificate/diploma",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes",
    )


class EducationNestedUpdate(BaseModel):
    """Schema for updating an education within a composite operation."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(
        default=None,
        description="Education ID (required for update, omit for create, send only ID to keep unchanged)",
    )
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
        description="Total workload in hours (for courses)",
    )
    certificate_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL to certificate/diploma",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes",
    )


# =============================================================================
# Qualification nested schemas (with specialties and educations)
# =============================================================================


class QualificationNestedCreate(BaseModel):
    """Schema for creating a qualification with nested specialties and educations."""

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
        description="State where the council registration is valid (e.g., SP, RJ)",
    )

    # Nested entities
    specialties: list[SpecialtyNestedCreate] = Field(
        default_factory=list,
        description="Specialties for this qualification",
    )
    educations: list[EducationNestedCreate] = Field(
        default_factory=list,
        description="Education records for this qualification",
    )


class QualificationNestedUpdate(BaseModel):
    """Schema for updating a qualification with nested specialties and educations."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(
        default=None,
        description="Qualification ID (required for update, omit for create)",
    )
    professional_type: Optional[ProfessionalType] = Field(
        default=None,
        description="Type of healthcare professional (immutable for updates)",
    )
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
    council_type: Optional[CouncilType] = Field(
        default=None,
        description="Council type (immutable for updates)",
    )
    council_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Council registration number",
    )
    council_state: Optional[StateUF] = Field(
        default=None,
        description="State where the council registration is valid (e.g., SP, RJ)",
    )

    # Nested entities (partial update: update existing, create new, delete missing)
    specialties: Optional[list[SpecialtyNestedUpdate]] = Field(
        default=None,
        description="Specialties for this qualification (null = no changes, [] = remove all)",
    )
    educations: Optional[list[EducationNestedUpdate]] = Field(
        default=None,
        description="Education records for this qualification (null = no changes, [] = remove all)",
    )


# =============================================================================
# Professional composite schemas (root level)
# =============================================================================


class OrganizationProfessionalCompositeCreate(BaseModel):
    """
    Schema for creating a professional with one qualification and nested entities.

    Creates in a single transaction:
    - Professional (basic info + address)
    - One qualification (council registration)
    - Specialties for the qualification
    - Educations for the qualification
    """

    model_config = ConfigDict(from_attributes=True)

    # Personal data
    full_name: str = Field(
        max_length=255,
        description="Professional's full name",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Professional's email address",
    )
    phone: Optional[Phone] = Field(
        default=None,
        description="Phone number (E.164 format)",
    )
    cpf: Optional[CPF] = Field(
        default=None,
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
    avatar_url: Optional[HttpUrl] = Field(
        default=None,
        description="Profile picture URL",
    )

    # Address fields (required)
    city: str = Field(max_length=100, description="City name")
    state_code: StateUF = Field(description="State code (e.g., SP, RJ)")
    postal_code: str = Field(max_length=10, description="Postal code (CEP)")

    # Address fields (optional)
    address: Optional[str] = Field(default=None, max_length=255)
    number: Optional[str] = Field(default=None, max_length=20)
    complement: Optional[str] = Field(default=None, max_length=100)
    neighborhood: Optional[str] = Field(default=None, max_length=100)

    # Nested qualification (exactly one)
    qualification: QualificationNestedCreate = Field(
        description="The professional's qualification with specialties and educations",
    )


class OrganizationProfessionalCompositeUpdate(BaseModel):
    """
    Schema for updating a professional with qualification and nested entities.

    Supports partial updates with the following strategy:
    - Professional fields: PATCH semantics (only update provided fields)
    - Qualification: identified by ID, update provided fields
    - Specialties/Educations:
      - With ID: update existing entity
      - Without ID: create new entity
      - IDs not in list: soft delete (if not None)
      - None list: no changes to that entity type
    """

    model_config = ConfigDict(from_attributes=True)

    # Personal data (all optional for PATCH)
    full_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Professional's full name",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Professional's email address",
    )
    phone: Optional[Phone] = Field(
        default=None,
        description="Phone number (E.164 format)",
    )
    cpf: Optional[CPF] = Field(
        default=None,
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
    avatar_url: Optional[HttpUrl] = Field(
        default=None,
        description="Profile picture URL",
    )

    # Address fields (optional for PATCH)
    address: Optional[str] = Field(default=None, max_length=255)
    number: Optional[str] = Field(default=None, max_length=20)
    complement: Optional[str] = Field(default=None, max_length=100)
    neighborhood: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    state_code: Optional[StateUF] = Field(
        default=None, description="State code (e.g., SP, RJ)"
    )
    postal_code: Optional[str] = Field(default=None, max_length=10)

    # Nested qualification (optional - None means no changes)
    qualification: Optional[QualificationNestedUpdate] = Field(
        default=None,
        description="The professional's qualification with specialties and educations (null = no changes)",
    )
