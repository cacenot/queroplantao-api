"""Shared presentation dependencies."""

from src.app.dependencies.context import CurrentContext, OrganizationContext
from src.shared.presentation.dependencies.specialty import (
    GetSpecialtyByCodeUC,
    GetSpecialtyUC,
    ListSpecialtiesUC,
    SearchSpecialtiesUC,
    get_list_specialties_use_case,
    get_search_specialties_use_case,
    get_specialty_by_code_use_case,
    get_specialty_use_case,
)

__all__ = [
    # Context
    "CurrentContext",
    "OrganizationContext",
    # Specialty use cases
    "GetSpecialtyByCodeUC",
    "GetSpecialtyUC",
    "ListSpecialtiesUC",
    "SearchSpecialtiesUC",
    "get_list_specialties_use_case",
    "get_search_specialties_use_case",
    "get_specialty_by_code_use_case",
    "get_specialty_use_case",
]
