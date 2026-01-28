"""
Repositories for the professionals module.
"""

from src.modules.professionals.infrastructure.repositories.bank_account_repository import (
    BankAccountRepository,
)
from src.modules.professionals.infrastructure.repositories.company_repository import (
    CompanyRepository,
)
from src.modules.professionals.infrastructure.repositories.organization_professional_repository import (
    OrganizationProfessionalRepository,
)
from src.modules.professionals.infrastructure.repositories.professional_change_diff_repository import (
    ProfessionalChangeDiffRepository,
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
from src.modules.professionals.infrastructure.repositories.professional_version_repository import (
    ProfessionalVersionRepository,
)
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)

__all__ = [
    "BankAccountRepository",
    "CompanyRepository",
    "OrganizationProfessionalRepository",
    "ProfessionalChangeDiffRepository",
    "ProfessionalCompanyRepository",
    "ProfessionalDocumentRepository",
    "ProfessionalEducationRepository",
    "ProfessionalQualificationRepository",
    "ProfessionalSpecialtyRepository",
    "ProfessionalVersionRepository",
    "SpecialtyRepository",
]
