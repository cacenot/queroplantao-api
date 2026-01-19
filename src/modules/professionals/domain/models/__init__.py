"""
Professionals module models.
"""

from src.modules.professionals.domain.models.enums import (
    CouncilType,
    DocumentCategory,
    DocumentType,
    EducationLevel,
    Gender,
    MaritalStatus,
    ProfessionalType,
    ResidencyStatus,
)
from src.modules.professionals.domain.models.organization_professional import (
    OrganizationProfessional,
    OrganizationProfessionalBase,
)
from src.modules.professionals.domain.models.professional_company import (
    ProfessionalCompany,
    ProfessionalCompanyBase,
)
from src.modules.professionals.domain.models.professional_document import (
    ProfessionalDocument,
    ProfessionalDocumentBase,
)
from src.modules.professionals.domain.models.professional_education import (
    ProfessionalEducation,
    ProfessionalEducationBase,
)
from src.modules.professionals.domain.models.professional_qualification import (
    ProfessionalQualification,
    ProfessionalQualificationBase,
)
from src.modules.professionals.domain.models.professional_specialty import (
    ProfessionalSpecialty,
    ProfessionalSpecialtyBase,
)
from src.modules.professionals.domain.models.specialty import Specialty, SpecialtyBase

__all__ = [
    # Enums
    "CouncilType",
    "DocumentCategory",
    "DocumentType",
    "EducationLevel",
    "Gender",
    "MaritalStatus",
    "ProfessionalType",
    "ResidencyStatus",
    # Base schemas
    "OrganizationProfessionalBase",
    "ProfessionalCompanyBase",
    "ProfessionalDocumentBase",
    "ProfessionalEducationBase",
    "ProfessionalQualificationBase",
    "ProfessionalSpecialtyBase",
    "SpecialtyBase",
    # Table models
    "OrganizationProfessional",
    "ProfessionalCompany",
    "ProfessionalDocument",
    "ProfessionalEducation",
    "ProfessionalQualification",
    "ProfessionalSpecialty",
    "Specialty",
]
