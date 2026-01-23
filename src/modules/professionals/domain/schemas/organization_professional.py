"""Schemas for OrganizationProfessional."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.modules.professionals.domain.models import Gender, MaritalStatus
from src.shared.domain.value_objects import StateUF

if TYPE_CHECKING:
    from src.modules.professionals.domain.schemas.professional_company import (
        ProfessionalCompanyDetailResponse,
    )
    from src.modules.professionals.domain.schemas.professional_document import (
        ProfessionalDocumentResponse,
    )
    from src.modules.professionals.domain.schemas.professional_qualification import (
        ProfessionalQualificationDetailResponse,
    )
    from src.shared.domain.schemas.bank_account import BankAccountResponse


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
    state_code: StateUF = Field(description="State code (e.g., SP, RJ)")
    postal_code: str = Field(max_length=10, description="Postal code (CEP)")

    # Address fields (optional)
    address: Optional[str] = Field(default=None, max_length=255)
    number: Optional[str] = Field(default=None, max_length=20)
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

    # Address fields
    address: Optional[str] = Field(default=None, max_length=255)
    number: Optional[str] = Field(default=None, max_length=20)
    complement: Optional[str] = Field(default=None, max_length=100)
    neighborhood: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    state_code: Optional[StateUF] = Field(default=None)
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

    # Address fields
    address: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None

    # Verification
    verified_at: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrganizationProfessionalDetailResponse(BaseModel):
    """
    Schema for organization professional with all nested data.

    Includes:
    - qualifications with specialties (including specialty info), educations, and documents
    - documents (profile-level only - qualification_id and specialty_id are None)
    - professional_companies with company details and bank accounts
    - bank_accounts (professional's direct bank accounts)
    """

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

    # Address fields
    address: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None

    # Nested relations
    qualifications: list["ProfessionalQualificationDetailResponse"] = []
    documents: list["ProfessionalDocumentResponse"] = []  # Profile-level documents only
    companies: list["ProfessionalCompanyDetailResponse"] = []
    bank_accounts: list["BankAccountResponse"] = []

    # Verification
    verified_at: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_model(
        cls, professional: "OrganizationProfessional"
    ) -> "OrganizationProfessionalDetailResponse":
        """
        Create response from model with proper document filtering.

        Profile-level documents have qualification_id=None and specialty_id=None.
        Documents with qualification_id or specialty_id are nested under their
        respective parent objects.
        """
        from src.modules.professionals.domain.schemas.professional_company import (
            ProfessionalCompanyDetailResponse,
        )
        from src.modules.professionals.domain.schemas.professional_document import (
            ProfessionalDocumentResponse,
        )
        from src.modules.professionals.domain.schemas.professional_qualification import (
            ProfessionalQualificationDetailResponse,
        )
        from src.shared.domain.schemas.bank_account import BankAccountResponse

        # Filter profile-level documents (not linked to qualification or specialty)
        profile_documents = [
            ProfessionalDocumentResponse.model_validate(doc)
            for doc in professional.documents
            if doc.qualification_id is None and doc.specialty_id is None
        ]

        return cls(
            id=professional.id,
            organization_id=professional.organization_id,
            full_name=professional.full_name,
            email=professional.email,
            phone=professional.phone,
            cpf=professional.cpf,
            birth_date=professional.birth_date,
            nationality=professional.nationality,
            gender=professional.gender,
            marital_status=professional.marital_status,
            avatar_url=professional.avatar_url,
            address=professional.address,
            number=professional.number,
            complement=professional.complement,
            neighborhood=professional.neighborhood,
            city=professional.city,
            state_code=professional.state_code,
            postal_code=professional.postal_code,
            qualifications=[
                ProfessionalQualificationDetailResponse.model_validate(q)
                for q in professional.qualifications
            ],
            documents=profile_documents,
            companies=[
                ProfessionalCompanyDetailResponse.model_validate(pc)
                for pc in professional.professional_companies
            ],
            bank_accounts=[
                BankAccountResponse.model_validate(ba)
                for ba in professional.bank_accounts
            ],
            verified_at=professional.verified_at,
            created_at=professional.created_at,
            updated_at=professional.updated_at,
        )


# Type import for from_model method type hints
from src.modules.professionals.domain.models import (  # noqa: E402
    OrganizationProfessional,
)

# Deferred imports to avoid circular imports
from src.modules.professionals.domain.schemas.professional_company import (  # noqa: E402
    ProfessionalCompanyDetailResponse,
)
from src.modules.professionals.domain.schemas.professional_document import (  # noqa: E402
    ProfessionalDocumentResponse,
)
from src.modules.professionals.domain.schemas.professional_qualification import (  # noqa: E402
    ProfessionalQualificationDetailResponse,
)
from src.shared.domain.schemas.bank_account import BankAccountResponse  # noqa: E402

OrganizationProfessionalDetailResponse.model_rebuild()


class QualificationSummary(BaseModel):
    """Summary of the primary professional qualification."""

    model_config = ConfigDict(from_attributes=True)

    professional_type: str
    council_type: str
    council_number: str
    council_state: str
    is_generalist: bool = Field(
        default=False,
        description="True if professional is a doctor with no specialties (clínico geral)",
    )


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
