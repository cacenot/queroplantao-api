"""
Filters and sorting for ProfessionalQualification entity.
"""

from typing import Optional

from pydantic import Field
from fastapi_restkit.filters import BooleanFilter, ListFilter, SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet

from src.modules.professionals.domain.models import CouncilType, ProfessionalType


class ProfessionalQualificationFilter(FilterSet):
    """
    Filter for ProfessionalQualification queries.

    Supports:
    - search: Search across council_number
    - professional_type: Filter by professional type (DOCTOR, NURSE, etc.)
    - council_type: Filter by council type (CRM, COREN, etc.)
    - council_state: Filter by council state (UF)
    - is_primary: Filter by primary qualification flag
    - is_verified: Filter by verification status
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by council number (partial, case-insensitive)",
    )

    professional_type: Optional[ListFilter[ProfessionalType]] = Field(
        default=None,
        description="Filter by professional type (DOCTOR, NURSE, etc.)",
    )

    council_type: Optional[ListFilter[CouncilType]] = Field(
        default=None,
        description="Filter by council type (CRM, COREN, etc.)",
    )

    council_state: Optional[SearchFilter] = Field(
        default=None,
        description="Filter by council state (2-char UF)",
    )

    is_primary: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by primary qualification flag",
    )

    is_verified: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by verification status",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["council_number"],
        }


class ProfessionalQualificationSorting(SortingSet):
    """
    Sorting options for ProfessionalQualification.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    professional_type: SortableField = SortableField(description="Professional type")
    council_state: SortableField = SortableField(description="Council state")
    graduation_year: SortableField = SortableField(description="Graduation year")
    created_at: SortableField = SortableField(description="Creation date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["id:asc"]
