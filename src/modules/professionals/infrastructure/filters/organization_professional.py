"""
Filters and sorting for OrganizationProfessional entity.
"""

from typing import Optional

from pydantic import Field
from fastapi_restkit.filters import ListFilter, SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet

from src.modules.professionals.domain.models import (
    Gender,
    MaritalStatus,
    ProfessionalType,
)


class OrganizationProfessionalFilter(FilterSet):
    """
    Filter for OrganizationProfessional queries.

    Supports:
    - search: Full-text search across full_name, email, cpf (using pg_trgm)
    - gender: Filter by gender
    - marital_status: Filter by marital status
    - professional_type: Filter by professional type (DOCTOR, NURSE, etc.)
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by name, email or CPF (partial, case-insensitive)",
    )

    gender: Optional[ListFilter[Gender]] = Field(
        default=None,
        description="Filter by gender (MALE, FEMALE)",
    )

    marital_status: Optional[ListFilter[MaritalStatus]] = Field(
        default=None,
        description="Filter by marital status",
    )

    professional_type: Optional[ListFilter[ProfessionalType]] = Field(
        default=None,
        description="Filter by professional type (DOCTOR, NURSE, NURSING_TECH, etc.)",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["full_name", "email", "cpf"],
        }


class OrganizationProfessionalSorting(SortingSet):
    """
    Sorting options for OrganizationProfessional.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    full_name: SortableField = SortableField(description="Full name")
    email: SortableField = SortableField(description="Email")
    created_at: SortableField = SortableField(description="Creation date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["id:asc"]
