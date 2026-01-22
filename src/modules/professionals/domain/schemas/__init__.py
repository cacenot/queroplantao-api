"""
Schemas for the professionals module.
"""

from src.modules.professionals.domain.schemas.organization_professional import (
    OrganizationProfessionalCreate,
    OrganizationProfessionalListItem,
    OrganizationProfessionalResponse,
    OrganizationProfessionalUpdate,
    QualificationSummary,
    SpecialtySummary,
)
from src.modules.professionals.domain.schemas.professional_company import (
    CompanyInfo,
    ProfessionalCompanyCreate,
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
    ProfessionalQualificationResponse,
    ProfessionalQualificationUpdate,
)
from src.modules.professionals.domain.schemas.professional_specialty import (
    ProfessionalSpecialtyCreate,
    ProfessionalSpecialtyResponse,
    ProfessionalSpecialtyUpdate,
    SpecialtyInfo,
)
from src.shared.domain.schemas.specialty import (
    SpecialtyListResponse,
    SpecialtyResponse,
)

__all__ = [
    # OrganizationProfessional
    "OrganizationProfessionalCreate",
    "OrganizationProfessionalUpdate",
    "OrganizationProfessionalResponse",
    "OrganizationProfessionalListItem",
    "QualificationSummary",
    "SpecialtySummary",
    # ProfessionalQualification
    "ProfessionalQualificationCreate",
    "ProfessionalQualificationUpdate",
    "ProfessionalQualificationResponse",
    # ProfessionalSpecialty
    "ProfessionalSpecialtyCreate",
    "ProfessionalSpecialtyUpdate",
    "ProfessionalSpecialtyResponse",
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
    "CompanyInfo",
    # Specialty
    "SpecialtyResponse",
    "SpecialtyListResponse",
]
