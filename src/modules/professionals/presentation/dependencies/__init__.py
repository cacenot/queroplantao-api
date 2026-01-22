"""Dependencies for the professionals presentation layer."""

# Context dependencies (from app)
from src.app.dependencies import (
    CurrentContext,
    OrganizationContext,
)

# OrganizationProfessional use case dependencies
from src.modules.professionals.presentation.dependencies.organization_professional import (
    CreateOrganizationProfessionalUC,
    DeleteOrganizationProfessionalUC,
    GetOrganizationProfessionalUC,
    ListOrganizationProfessionalsUC,
    ListOrganizationProfessionalsSummaryUC,
    UpdateOrganizationProfessionalUC,
)

# ProfessionalCompany use case dependencies
from src.modules.professionals.presentation.dependencies.professional_company import (
    CreateProfessionalCompanyUC,
    DeleteProfessionalCompanyUC,
    GetProfessionalCompanyUC,
    ListProfessionalCompaniesUC,
    UpdateProfessionalCompanyUC,
)

# ProfessionalDocument use case dependencies
from src.modules.professionals.presentation.dependencies.professional_document import (
    CreateProfessionalDocumentUC,
    DeleteProfessionalDocumentUC,
    GetProfessionalDocumentUC,
    ListProfessionalDocumentsUC,
    UpdateProfessionalDocumentUC,
)

# ProfessionalEducation use case dependencies
from src.modules.professionals.presentation.dependencies.professional_education import (
    CreateProfessionalEducationUC,
    DeleteProfessionalEducationUC,
    GetProfessionalEducationUC,
    ListProfessionalEducationsUC,
    UpdateProfessionalEducationUC,
)

# ProfessionalQualification use case dependencies
from src.modules.professionals.presentation.dependencies.professional_qualification import (
    CreateProfessionalQualificationUC,
    DeleteProfessionalQualificationUC,
    GetProfessionalQualificationUC,
    ListProfessionalQualificationsUC,
    UpdateProfessionalQualificationUC,
)

# ProfessionalSpecialty use case dependencies
from src.modules.professionals.presentation.dependencies.professional_specialty import (
    CreateProfessionalSpecialtyUC,
    DeleteProfessionalSpecialtyUC,
    GetProfessionalSpecialtyUC,
    ListProfessionalSpecialtiesUC,
    UpdateProfessionalSpecialtyUC,
)


__all__ = [
    # Context
    "CurrentContext",
    "OrganizationContext",
    # OrganizationProfessional
    "CreateOrganizationProfessionalUC",
    "UpdateOrganizationProfessionalUC",
    "DeleteOrganizationProfessionalUC",
    "GetOrganizationProfessionalUC",
    "ListOrganizationProfessionalsUC",
    "ListOrganizationProfessionalsSummaryUC",
    # ProfessionalCompany
    "CreateProfessionalCompanyUC",
    "UpdateProfessionalCompanyUC",
    "DeleteProfessionalCompanyUC",
    "GetProfessionalCompanyUC",
    "ListProfessionalCompaniesUC",
    # ProfessionalDocument
    "CreateProfessionalDocumentUC",
    "UpdateProfessionalDocumentUC",
    "DeleteProfessionalDocumentUC",
    "GetProfessionalDocumentUC",
    "ListProfessionalDocumentsUC",
    # ProfessionalEducation
    "CreateProfessionalEducationUC",
    "UpdateProfessionalEducationUC",
    "DeleteProfessionalEducationUC",
    "GetProfessionalEducationUC",
    "ListProfessionalEducationsUC",
    # ProfessionalQualification
    "CreateProfessionalQualificationUC",
    "UpdateProfessionalQualificationUC",
    "DeleteProfessionalQualificationUC",
    "GetProfessionalQualificationUC",
    "ListProfessionalQualificationsUC",
    # ProfessionalSpecialty
    "CreateProfessionalSpecialtyUC",
    "UpdateProfessionalSpecialtyUC",
    "DeleteProfessionalSpecialtyUC",
    "GetProfessionalSpecialtyUC",
    "ListProfessionalSpecialtiesUC",
]
