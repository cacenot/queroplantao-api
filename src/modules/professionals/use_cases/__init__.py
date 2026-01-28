"""
Use cases for the professionals module.
"""

# OrganizationProfessional use cases
from src.modules.professionals.use_cases.organization_professional import (
    CreateOrganizationProfessionalCompositeUseCase,
    CreateOrganizationProfessionalUseCase,
    DeleteOrganizationProfessionalUseCase,
    GetOrganizationProfessionalUseCase,
    ListOrganizationProfessionalsUseCase,
    ListOrganizationProfessionalsSummaryUseCase,
    UpdateOrganizationProfessionalCompositeUseCase,
    UpdateOrganizationProfessionalUseCase,
)

# ProfessionalCompany use cases
from src.modules.professionals.use_cases.professional_company import (
    CreateProfessionalCompanyUseCase,
    DeleteProfessionalCompanyUseCase,
    GetProfessionalCompanyUseCase,
    ListProfessionalCompaniesUseCase,
    UpdateProfessionalCompanyUseCase,
)

# ProfessionalDocument use cases
from src.modules.professionals.use_cases.professional_document import (
    CreateProfessionalDocumentUseCase,
    DeleteProfessionalDocumentUseCase,
    GetProfessionalDocumentUseCase,
    ListProfessionalDocumentsUseCase,
    UpdateProfessionalDocumentUseCase,
)

# ProfessionalEducation use cases
from src.modules.professionals.use_cases.professional_education import (
    CreateProfessionalEducationUseCase,
    DeleteProfessionalEducationUseCase,
    GetProfessionalEducationUseCase,
    ListProfessionalEducationsUseCase,
    UpdateProfessionalEducationUseCase,
)

# ProfessionalQualification use cases
from src.modules.professionals.use_cases.professional_qualification import (
    CreateProfessionalQualificationUseCase,
    DeleteProfessionalQualificationUseCase,
    GetProfessionalQualificationUseCase,
    ListProfessionalQualificationsUseCase,
    UpdateProfessionalQualificationUseCase,
)

# ProfessionalSpecialty use cases
from src.modules.professionals.use_cases.professional_specialty import (
    CreateProfessionalSpecialtyUseCase,
    DeleteProfessionalSpecialtyUseCase,
    GetProfessionalSpecialtyUseCase,
    ListProfessionalSpecialtiesUseCase,
    UpdateProfessionalSpecialtyUseCase,
)

# ProfessionalVersion use cases
from src.modules.professionals.use_cases.professional_version import (
    ApplyProfessionalVersionUseCase,
    CreateProfessionalVersionUseCase,
    DiffCalculatorService,
    GetProfessionalVersionUseCase,
    ListProfessionalVersionsUseCase,
    RejectProfessionalVersionUseCase,
    SnapshotApplierService,
    SnapshotBuilderService,
)

# Shared services
from src.modules.professionals.use_cases.shared import (
    BankAccountSyncService,
    CompanySyncService,
    QualificationSyncService,
)

# Specialty use cases (read-only for tenants)
from src.shared.use_cases.specialty import (
    GetSpecialtyByCodeUseCase,
    GetSpecialtyUseCase,
    ListSpecialtiesUseCase,
    SearchSpecialtiesUseCase,
)

__all__ = [
    # OrganizationProfessional
    "CreateOrganizationProfessionalCompositeUseCase",
    "CreateOrganizationProfessionalUseCase",
    "UpdateOrganizationProfessionalCompositeUseCase",
    "UpdateOrganizationProfessionalUseCase",
    "DeleteOrganizationProfessionalUseCase",
    "GetOrganizationProfessionalUseCase",
    "ListOrganizationProfessionalsUseCase",
    "ListOrganizationProfessionalsSummaryUseCase",
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
    # ProfessionalVersion
    "CreateProfessionalVersionUseCase",
    "ApplyProfessionalVersionUseCase",
    "RejectProfessionalVersionUseCase",
    "GetProfessionalVersionUseCase",
    "ListProfessionalVersionsUseCase",
    "DiffCalculatorService",
    "SnapshotApplierService",
    "SnapshotBuilderService",
    # Shared services
    "BankAccountSyncService",
    "CompanySyncService",
    "QualificationSyncService",
    # Specialty (read-only)
    "GetSpecialtyUseCase",
    "GetSpecialtyByCodeUseCase",
    "ListSpecialtiesUseCase",
    "SearchSpecialtiesUseCase",
]
