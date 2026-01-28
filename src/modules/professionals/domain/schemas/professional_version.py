"""Schemas for professional versioning.

These schemas are used for API input validation and response formatting.
They mirror the TypedDict structure in version_snapshot.py but add Pydantic validation.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from src.modules.professionals.domain.models.enums import (
    CouncilType,
    EducationLevel,
    Gender,
    MaritalStatus,
    ProfessionalType,
    ResidencyStatus,
)
from src.modules.screening.domain.models.enums import ChangeType, SourceType
from src.shared.domain.models.enums import PixKeyType
from src.shared.domain.value_objects import CNPJ, CPF, CPFOrCNPJ, Phone, StateUF


# =============================================================================
# Input Schemas (for creating versions)
# =============================================================================


class PersonalInfoInput(BaseModel):
    """Input schema for professional personal information."""

    model_config = ConfigDict(from_attributes=True)

    # Required fields
    full_name: str = Field(max_length=255, description="Professional's full name")

    # Optional personal data
    email: Optional[EmailStr] = Field(default=None, description="Email address")
    phone: Optional[Phone] = Field(default=None, description="Phone (E.164 format)")
    cpf: Optional[CPF] = Field(default=None, description="CPF (11 digits)")
    birth_date: Optional[date] = Field(default=None, description="Date of birth")
    nationality: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[Gender] = Field(default=None)
    marital_status: Optional[MaritalStatus] = Field(default=None)
    avatar_url: Optional[HttpUrl] = Field(default=None, description="Profile picture")

    # Address fields
    address: Optional[str] = Field(default=None, max_length=255)
    number: Optional[str] = Field(default=None, max_length=20)
    complement: Optional[str] = Field(default=None, max_length=100)
    neighborhood: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    state_code: Optional[StateUF] = Field(default=None)
    postal_code: Optional[str] = Field(default=None, max_length=10)

    # Verification status
    is_verified: bool = Field(default=False)


class SpecialtyInput(BaseModel):
    """Input schema for professional specialty."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, description="Existing specialty link ID")
    specialty_id: UUID = Field(description="Reference to global specialty")
    is_primary: bool = Field(default=False)
    rqe_number: Optional[str] = Field(default=None, max_length=20)
    rqe_state: Optional[StateUF] = Field(default=None)
    residency_status: Optional[ResidencyStatus] = Field(default=None)
    residency_institution: Optional[str] = Field(default=None, max_length=255)
    residency_expected_completion: Optional[date] = Field(default=None)
    certificate_url: Optional[HttpUrl] = Field(default=None)


class EducationInput(BaseModel):
    """Input schema for professional education."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, description="Existing education ID")
    level: EducationLevel = Field(description="Education level")
    course_name: str = Field(max_length=255)
    institution: str = Field(max_length=255)
    start_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    end_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    is_completed: bool = Field(default=False)
    workload_hours: Optional[int] = Field(default=None, ge=0)
    certificate_url: Optional[HttpUrl] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=2000)


class QualificationInput(BaseModel):
    """Input schema for professional qualification with nested entities."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, description="Existing qualification ID")
    professional_type: ProfessionalType = Field(description="Type of professional")
    is_primary: bool = Field(default=False)
    graduation_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    council_type: CouncilType = Field(description="Council type")
    council_number: str = Field(max_length=50)
    council_state: StateUF = Field(description="Council state")

    # Nested entities
    specialties: list[SpecialtyInput] = Field(default_factory=list)
    educations: list[EducationInput] = Field(default_factory=list)


class CompanyInput(BaseModel):
    """Input schema for professional company."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(
        default=None, description="Existing ProfessionalCompany ID"
    )
    company_id: Optional[UUID] = Field(default=None, description="Existing Company ID")
    cnpj: CNPJ = Field(description="CNPJ (14 digits)")
    razao_social: str = Field(max_length=255)
    nome_fantasia: Optional[str] = Field(default=None, max_length=255)
    inscricao_estadual: Optional[str] = Field(default=None, max_length=20)
    inscricao_municipal: Optional[str] = Field(default=None, max_length=20)

    # Address
    address: Optional[str] = Field(default=None, max_length=255)
    number: Optional[str] = Field(default=None, max_length=20)
    complement: Optional[str] = Field(default=None, max_length=100)
    neighborhood: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    state_code: Optional[StateUF] = Field(default=None)
    postal_code: Optional[str] = Field(default=None, max_length=10)

    # Metadata
    started_at: Optional[date] = Field(default=None)
    ended_at: Optional[date] = Field(default=None)


class BankAccountInput(BaseModel):
    """Input schema for bank account."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, description="Existing bank account ID")
    bank_code: str = Field(max_length=10, description="Bank code")
    agency_number: str = Field(max_length=10)
    agency_digit: Optional[str] = Field(default=None, max_length=2)
    account_number: str = Field(max_length=20)
    account_digit: Optional[str] = Field(default=None, max_length=2)
    account_holder_name: str = Field(max_length=255)
    account_holder_document: CPFOrCNPJ = Field(description="CPF (11) or CNPJ (14)")
    pix_key_type: Optional[PixKeyType] = Field(default=None)
    pix_key: Optional[str] = Field(default=None, max_length=100)
    is_primary: bool = Field(default=False)
    is_company_account: bool = Field(default=False)


class ProfessionalVersionCreate(BaseModel):
    """Schema for creating a new professional version."""

    model_config = ConfigDict(from_attributes=True)

    # Personal info (required for initial creation, optional for updates)
    personal_info: Optional[PersonalInfoInput] = Field(
        default=None, description="Professional personal information"
    )

    # Optional collections
    qualifications: list[QualificationInput] = Field(
        default_factory=list, description="Professional qualifications"
    )
    companies: list[CompanyInput] = Field(
        default_factory=list, description="Professional companies"
    )
    bank_accounts: list[BankAccountInput] = Field(
        default_factory=list, description="Bank accounts"
    )

    # Source information
    source_type: SourceType = Field(
        default=SourceType.DIRECT, description="How this version was created"
    )
    source_id: Optional[UUID] = Field(
        default=None, description="ID of the source entity (e.g., ScreeningProcess ID)"
    )

    # Notes
    notes: Optional[str] = Field(
        default=None, max_length=2000, description="Notes about this version"
    )


class ProfessionalVersionReject(BaseModel):
    """Schema for rejecting a professional version."""

    model_config = ConfigDict(from_attributes=True)

    rejection_reason: str = Field(max_length=2000, description="Reason for rejection")


# =============================================================================
# Response Schemas
# =============================================================================


class ProfessionalChangeDiffResponse(BaseModel):
    """Response schema for a single change diff."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    field_path: str
    change_type: ChangeType
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

    # Computed properties
    is_nested_change: bool = Field(description="Whether this is a nested entity change")
    root_field: str = Field(description="Root field name")


class ProfessionalVersionResponse(BaseModel):
    """Response schema for a professional version."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    professional_id: Optional[UUID] = None
    version_number: int
    data_snapshot: dict[str, Any]
    is_current: bool
    source_type: SourceType
    source_id: Optional[UUID] = None

    # Application status
    applied_at: Optional[datetime] = None
    applied_by: Optional[UUID] = None

    # Rejection info
    rejected_at: Optional[datetime] = None
    rejected_by: Optional[UUID] = None
    rejection_reason: Optional[str] = None

    # Notes
    notes: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    # Computed properties
    is_applied: bool
    is_rejected: bool
    is_pending: bool
    is_from_screening: bool


class ProfessionalVersionDetailResponse(ProfessionalVersionResponse):
    """Detailed response schema including diffs."""

    diffs: list[ProfessionalChangeDiffResponse] = Field(default_factory=list)


class ProfessionalVersionListResponse(BaseModel):
    """Response schema for version list item."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_number: int
    is_current: bool
    source_type: SourceType
    applied_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime

    # Computed
    is_applied: bool
    is_rejected: bool
    is_pending: bool
    changes_count: int = Field(description="Number of changes in this version")
