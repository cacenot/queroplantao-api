"""TypedDict definitions for professional version snapshots.

These types define the structure of the data_snapshot JSONB field
in ProfessionalVersion. They mirror the composite schemas but are
designed for storage/audit rather than validation.

The snapshot structure follows the composite schema pattern:
{
    "personal_info": {...},
    "qualifications": [
        {
            ...qualification fields...,
            "specialties": [...],
            "educations": [...]
        }
    ],
    "companies": [...],
    "bank_accounts": [...]
}
"""

from typing import TypedDict


class PersonalInfoSnapshot(TypedDict, total=False):
    """Snapshot of professional personal information."""

    # Required fields
    full_name: str

    # Optional personal data
    email: str | None
    phone: str | None
    cpf: str | None
    birth_date: str | None
    nationality: str | None
    gender: str | None  # Gender enum value
    marital_status: str | None  # MaritalStatus enum value
    avatar_url: str | None

    # Address fields
    address: str | None
    number: str | None
    complement: str | None
    neighborhood: str | None
    city: str | None
    state_code: str | None  # StateUF value
    postal_code: str | None

    # Metadata
    is_verified: bool
    verified_at: str | None


class SpecialtySnapshot(TypedDict, total=False):
    """Snapshot of a professional specialty."""

    id: str  # UUID as string
    specialty_id: str  # Reference to global specialty
    specialty_name: str  # Denormalized for readability
    is_primary: bool
    rqe_number: str | None
    rqe_state: str | None
    residency_status: str | None  # ResidencyStatus enum value
    residency_institution: str | None
    residency_expected_completion: str | None
    certificate_url: str | None


class EducationSnapshot(TypedDict, total=False):
    """Snapshot of a professional education record."""

    id: str  # UUID as string
    level: str  # EducationLevel enum value
    course_name: str
    institution: str
    start_year: int | None
    end_year: int | None
    is_completed: bool
    workload_hours: int | None
    certificate_url: str | None
    notes: str | None


class QualificationSnapshot(TypedDict, total=False):
    """Snapshot of a professional qualification with nested entities."""

    id: str  # UUID as string
    professional_type: str  # ProfessionalType enum value
    is_primary: bool
    graduation_year: int | None
    council_type: str  # CouncilType enum value
    council_number: str
    council_state: str  # StateUF value

    # Nested entities
    specialties: list[SpecialtySnapshot]
    educations: list[EducationSnapshot]


class CompanySnapshot(TypedDict, total=False):
    """Snapshot of a professional's company."""

    id: str  # UUID as string (ProfessionalCompany ID)
    company_id: str  # Reference to Company
    cnpj: str
    razao_social: str
    nome_fantasia: str | None
    inscricao_estadual: str | None
    inscricao_municipal: str | None

    # Address
    address: str | None
    number: str | None
    complement: str | None
    neighborhood: str | None
    city: str | None
    state_code: str | None
    postal_code: str | None

    # Metadata
    started_at: str | None
    ended_at: str | None


class BankAccountSnapshot(TypedDict, total=False):
    """Snapshot of a bank account."""

    id: str  # UUID as string
    bank_code: str
    bank_name: str | None
    agency_number: str
    agency_digit: str | None
    account_number: str
    account_digit: str | None
    account_holder_name: str
    account_holder_document: str  # CPF or CNPJ
    pix_key_type: str | None
    pix_key: str | None
    is_primary: bool
    is_company_account: bool


class ProfessionalDataSnapshot(TypedDict, total=False):
    """
    Complete snapshot of professional data.

    This is the root type stored in ProfessionalVersion.data_snapshot.
    It contains all data that can be versioned for a professional.
    """

    # Professional personal info
    personal_info: PersonalInfoSnapshot

    # Professional qualifications (with nested specialties/educations)
    qualifications: list[QualificationSnapshot]

    # Payment-related data
    companies: list[CompanySnapshot]
    bank_accounts: list[BankAccountSnapshot]


# Type alias for the complete snapshot
DataSnapshot = ProfessionalDataSnapshot
