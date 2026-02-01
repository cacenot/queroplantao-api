"""
Filters and sorting for ProfessionalSpecialty entity.
"""

from typing import Optional
from uuid import UUID

from pydantic import Field
from fastapi_restkit.filters import BooleanFilter, ListFilter, SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet


class ProfessionalSpecialtyFilter(FilterSet):
    """
    Filter for ProfessionalSpecialty queries.

    Supports:
    - search: Search across RQE number
    - is_verified: Filter by verification status
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by RQE number (partial, case-insensitive)",
    )

    qualification_id: Optional[ListFilter[UUID]] = Field(
        default=None,
        description="Filter by qualification ID",
    )

    is_verified: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by verification status",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["rqe_number"],
        }


class ProfessionalSpecialtySorting(SortingSet):
    """
    Sorting options for ProfessionalSpecialty.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    acquisition_date: SortableField = SortableField(description="Acquisition date")
    created_at: SortableField = SortableField(description="Creation date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["id:asc"]
