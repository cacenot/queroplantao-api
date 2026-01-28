"""
Filters and sorting for professionals module.

Provides FilterSet and SortingSet classes for pagination with fastapi-restkit.
"""

from src.modules.professionals.infrastructure.filters.organization_professional import (
    OrganizationProfessionalFilter,
    OrganizationProfessionalSorting,
)
from src.modules.professionals.infrastructure.filters.professional_qualification import (
    ProfessionalQualificationFilter,
    ProfessionalQualificationSorting,
)
from src.modules.professionals.infrastructure.filters.professional_specialty import (
    ProfessionalSpecialtyFilter,
    ProfessionalSpecialtySorting,
)
from src.modules.professionals.infrastructure.filters.professional_education import (
    ProfessionalEducationFilter,
    ProfessionalEducationSorting,
)
from src.modules.professionals.infrastructure.filters.professional_document import (
    ProfessionalDocumentFilter,
    ProfessionalDocumentSorting,
)
from src.modules.professionals.infrastructure.filters.professional_company import (
    ProfessionalCompanyFilter,
    ProfessionalCompanySorting,
)
from src.modules.professionals.infrastructure.filters.professional_version_filters import (
    ProfessionalVersionFilter,
    ProfessionalVersionSorting,
)
from src.shared.infrastructure.filters.specialty import (
    SpecialtyFilter,
    SpecialtySorting,
)

__all__ = [
    # OrganizationProfessional
    "OrganizationProfessionalFilter",
    "OrganizationProfessionalSorting",
    # ProfessionalQualification
    "ProfessionalQualificationFilter",
    "ProfessionalQualificationSorting",
    # ProfessionalSpecialty
    "ProfessionalSpecialtyFilter",
    "ProfessionalSpecialtySorting",
    # ProfessionalEducation
    "ProfessionalEducationFilter",
    "ProfessionalEducationSorting",
    # ProfessionalDocument
    "ProfessionalDocumentFilter",
    "ProfessionalDocumentSorting",
    # ProfessionalCompany
    "ProfessionalCompanyFilter",
    "ProfessionalCompanySorting",
    # ProfessionalVersion
    "ProfessionalVersionFilter",
    "ProfessionalVersionSorting",
    # Specialty
    "SpecialtyFilter",
    "SpecialtySorting",
]
