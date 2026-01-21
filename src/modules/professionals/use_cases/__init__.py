"""
Use cases for the professionals module.
"""

# OrganizationProfessional use cases
from src.modules.professionals.use_cases.create_organization_professional import (
    CreateOrganizationProfessionalUseCase,
)
from src.modules.professionals.use_cases.delete_organization_professional import (
    DeleteOrganizationProfessionalUseCase,
)
from src.modules.professionals.use_cases.get_organization_professional import (
    GetOrganizationProfessionalUseCase,
)
from src.modules.professionals.use_cases.list_organization_professionals import (
    ListOrganizationProfessionalsUseCase,
)
from src.modules.professionals.use_cases.update_organization_professional import (
    UpdateOrganizationProfessionalUseCase,
)

# ProfessionalQualification use cases
from src.modules.professionals.use_cases.professional_qualification_use_cases import (
    CreateProfessionalQualificationUseCase,
    DeleteProfessionalQualificationUseCase,
    GetProfessionalQualificationUseCase,
    ListProfessionalQualificationsUseCase,
    UpdateProfessionalQualificationUseCase,
)

# ProfessionalSpecialty use cases
from src.modules.professionals.use_cases.professional_specialty_use_cases import (
    CreateProfessionalSpecialtyUseCase,
    DeleteProfessionalSpecialtyUseCase,
    GetProfessionalSpecialtyUseCase,
    ListProfessionalSpecialtiesUseCase,
    UpdateProfessionalSpecialtyUseCase,
)

# ProfessionalEducation use cases
from src.modules.professionals.use_cases.professional_education_use_cases import (
    CreateProfessionalEducationUseCase,
    DeleteProfessionalEducationUseCase,
    GetProfessionalEducationUseCase,
    ListProfessionalEducationsUseCase,
    UpdateProfessionalEducationUseCase,
)

# ProfessionalDocument use cases
from src.modules.professionals.use_cases.professional_document_use_cases import (
    CreateProfessionalDocumentUseCase,
    DeleteProfessionalDocumentUseCase,
    GetProfessionalDocumentUseCase,
    ListProfessionalDocumentsUseCase,
    UpdateProfessionalDocumentUseCase,
)

# ProfessionalCompany use cases
from src.modules.professionals.use_cases.professional_company_use_cases import (
    CreateProfessionalCompanyUseCase,
    DeleteProfessionalCompanyUseCase,
    GetProfessionalCompanyUseCase,
    ListProfessionalCompaniesUseCase,
    UpdateProfessionalCompanyUseCase,
)

# Specialty use cases (read-only for tenants)
from src.modules.professionals.use_cases.specialty_use_cases import (
    GetSpecialtyByCodeUseCase,
    GetSpecialtyUseCase,
    ListSpecialtiesUseCase,
    SearchSpecialtiesUseCase,
)

__all__ = [
    # OrganizationProfessional
    "CreateOrganizationProfessionalUseCase",
    "UpdateOrganizationProfessionalUseCase",
    "DeleteOrganizationProfessionalUseCase",
    "GetOrganizationProfessionalUseCase",
    "ListOrganizationProfessionalsUseCase",
    # ProfessionalQualification
    "CreateProfessionalQualificationUseCase",
    "UpdateProfessionalQualificationUseCase",
    "DeleteProfessionalQualificationUseCase",
    "GetProfessionalQualificationUseCase",
    "ListProfessionalQualificationsUseCase",
    # ProfessionalSpecialty
    "CreateProfessionalSpecialtyUseCase",
    "UpdateProfessionalSpecialtyUseCase",
    "DeleteProfessionalSpecialtyUseCase",
    "GetProfessionalSpecialtyUseCase",
    "ListProfessionalSpecialtiesUseCase",
    # ProfessionalEducation
    "CreateProfessionalEducationUseCase",
    "UpdateProfessionalEducationUseCase",
    "DeleteProfessionalEducationUseCase",
    "GetProfessionalEducationUseCase",
    "ListProfessionalEducationsUseCase",
    # ProfessionalDocument
    "CreateProfessionalDocumentUseCase",
    "UpdateProfessionalDocumentUseCase",
    "DeleteProfessionalDocumentUseCase",
    "GetProfessionalDocumentUseCase",
    "ListProfessionalDocumentsUseCase",
    # ProfessionalCompany
    "CreateProfessionalCompanyUseCase",
    "UpdateProfessionalCompanyUseCase",
    "DeleteProfessionalCompanyUseCase",
    "GetProfessionalCompanyUseCase",
    "ListProfessionalCompaniesUseCase",
    # Specialty (read-only)
    "GetSpecialtyUseCase",
    "GetSpecialtyByCodeUseCase",
    "ListSpecialtiesUseCase",
    "SearchSpecialtiesUseCase",
]
