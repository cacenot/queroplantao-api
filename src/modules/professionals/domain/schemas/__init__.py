"""
Schemas for the professionals module.
"""

from src.modules.professionals.domain.schemas.organization_professional import (
    OrganizationProfessionalCreate,
    OrganizationProfessionalDetailResponse,
    OrganizationProfessionalListItem,
    OrganizationProfessionalResponse,
    OrganizationProfessionalUpdate,
    QualificationSummary,
    SpecialtySummary,
)
from src.modules.professionals.domain.schemas.organization_professional_composite import (
    EducationNestedCreate,
    EducationNestedUpdate,
    OrganizationProfessionalCompositeCreate,
    OrganizationProfessionalCompositeUpdate,
    QualificationNestedCreate,
    QualificationNestedUpdate,
    SpecialtyNestedCreate,
    SpecialtyNestedUpdate,
)
from src.modules.professionals.domain.schemas.professional_company import (
    CompanyDetailInfo,
    CompanyInfo,
    ProfessionalCompanyCreate,
    ProfessionalCompanyDetailResponse,
    ProfessionalCompanyResponse,
    ProfessionalCompanyUpdate,
)
from src.modules.professionals.domain.schemas.professional_document import (
    ProfessionalDocumentCreate,
    ProfessionalDocumentResponse,
    ProfessionalDocumentUpdate,
)
from src.modules.professionals.domain.schemas.professional_education import (
    ProfessionalEducationCreate,
    ProfessionalEducationResponse,
    ProfessionalEducationUpdate,
)
from src.modules.professionals.domain.schemas.professional_qualification import (
    ProfessionalQualificationCreate,
    ProfessionalQualificationDetailResponse,
    ProfessionalQualificationResponse,
    ProfessionalQualificationUpdate,
)
from src.modules.professionals.domain.schemas.professional_specialty import (
    ProfessionalSpecialtyCreate,
    ProfessionalSpecialtyDetailResponse,
    ProfessionalSpecialtyResponse,
    ProfessionalSpecialtyUpdate,
    SpecialtyInfo,
)
from src.shared.domain.schemas.bank_account import (
    BankAccountResponse,
    BankInfo,
)
from src.shared.domain.schemas.specialty import (
    SpecialtyListResponse,
    SpecialtyResponse,
)

from src.modules.professionals.domain.schemas.professional_version import (
    BankAccountInput,
    CompanyInput,
    EducationInput,
    PersonalInfoInput,
    ProfessionalChangeDiffResponse,
    ProfessionalVersionCreate,
    ProfessionalVersionDetailResponse,
    ProfessionalVersionListResponse,
    ProfessionalVersionReject,
    ProfessionalVersionResponse,
    QualificationInput,
    SpecialtyInput,
)

__all__ = [
    # OrganizationProfessional
    "OrganizationProfessionalCreate",
    "OrganizationProfessionalUpdate",
    "OrganizationProfessionalResponse",
    "OrganizationProfessionalDetailResponse",
    "OrganizationProfessionalListItem",
    "QualificationSummary",
    "SpecialtySummary",
    # OrganizationProfessional Composite
    "OrganizationProfessionalCompositeCreate",
    "OrganizationProfessionalCompositeUpdate",
    "QualificationNestedCreate",
    "QualificationNestedUpdate",
    "SpecialtyNestedCreate",
    "SpecialtyNestedUpdate",
    "EducationNestedCreate",
    "EducationNestedUpdate",
    # ProfessionalQualification
    "ProfessionalQualificationCreate",
    "ProfessionalQualificationUpdate",
    "ProfessionalQualificationResponse",
    "ProfessionalQualificationDetailResponse",
    # ProfessionalSpecialty
    "ProfessionalSpecialtyCreate",
    "ProfessionalSpecialtyUpdate",
    "ProfessionalSpecialtyResponse",
    "ProfessionalSpecialtyDetailResponse",
    "SpecialtyInfo",
    # ProfessionalEducation
    "ProfessionalEducationCreate",
    "ProfessionalEducationUpdate",
    "ProfessionalEducationResponse",
    # ProfessionalDocument
    "ProfessionalDocumentCreate",
    "ProfessionalDocumentUpdate",
    "ProfessionalDocumentResponse",
    # ProfessionalCompany
    "ProfessionalCompanyCreate",
    "ProfessionalCompanyUpdate",
    "ProfessionalCompanyResponse",
    "ProfessionalCompanyDetailResponse",
    "CompanyInfo",
    "CompanyDetailInfo",
    # BankAccount
    "BankAccountResponse",
    "BankInfo",
    # Specialty
    "SpecialtyResponse",
    "SpecialtyListResponse",
    # ProfessionalVersion
    "PersonalInfoInput",
    "SpecialtyInput",
    "EducationInput",
    "QualificationInput",
    "CompanyInput",
    "BankAccountInput",
    "ProfessionalVersionCreate",
    "ProfessionalVersionReject",
    "ProfessionalChangeDiffResponse",
    "ProfessionalVersionResponse",
    "ProfessionalVersionDetailResponse",
    "ProfessionalVersionListResponse",
]
