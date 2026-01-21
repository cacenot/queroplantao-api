"""
Filters and sorting for Specialty entity (global reference data).
"""

from typing import Optional

from pydantic import Field
from fastapi_restkit.filters import SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet


class SpecialtyFilter(FilterSet):
    """
    Filter for Specialty queries.

    Supports:
    - search: Search across code, name (using pg_trgm for fuzzy matching)
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by code or name (partial, case-insensitive, accent-insensitive)",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["code", "name"],
        }


class SpecialtySorting(SortingSet):
    """
    Sorting options for Specialty.

    Default sorting is by name alphabetically.
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    code: SortableField = SortableField(description="Specialty code")
    name: SortableField = SortableField(description="Specialty name")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["name:asc"]
