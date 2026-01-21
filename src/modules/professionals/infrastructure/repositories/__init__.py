"""
Repositories for the professionals module.
"""

from src.modules.professionals.infrastructure.repositories.organization_professional_repository import (
    OrganizationProfessionalRepository,
)
from src.modules.professionals.infrastructure.repositories.professional_company_repository import (
    ProfessionalCompanyRepository,
)
from src.modules.professionals.infrastructure.repositories.professional_document_repository import (
    ProfessionalDocumentRepository,
)
from src.modules.professionals.infrastructure.repositories.professional_education_repository import (
    ProfessionalEducationRepository,
)
from src.modules.professionals.infrastructure.repositories.professional_qualification_repository import (
    ProfessionalQualificationRepository,
)
from src.modules.professionals.infrastructure.repositories.professional_specialty_repository import (
    ProfessionalSpecialtyRepository,
)
from src.modules.professionals.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)

__all__ = [
    "OrganizationProfessionalRepository",
    "ProfessionalCompanyRepository",
    "ProfessionalDocumentRepository",
    "ProfessionalEducationRepository",
    "ProfessionalQualificationRepository",
    "ProfessionalSpecialtyRepository",
    "SpecialtyRepository",
]
