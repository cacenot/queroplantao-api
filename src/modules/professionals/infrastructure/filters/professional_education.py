"""
Filters and sorting for ProfessionalEducation entity.
"""

from typing import Optional

from pydantic import Field
from fastapi_restkit.filters import BooleanFilter, ListFilter, SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet

from src.modules.professionals.domain.models import EducationLevel


class ProfessionalEducationFilter(FilterSet):
    """
    Filter for ProfessionalEducation queries.

    Supports:
    - search: Search across course_name, institution
    - level: Filter by education level
    - is_completed: Filter by completion status
    - is_verified: Filter by verification status
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by course name or institution (partial, case-insensitive)",
    )

    level: Optional[ListFilter[EducationLevel]] = Field(
        default=None,
        description="Filter by education level",
    )

    is_completed: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by completion status",
    )

    is_verified: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by verification status",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["course_name", "institution"],
        }


class ProfessionalEducationSorting(SortingSet):
    """
    Sorting options for ProfessionalEducation.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    level: SortableField = SortableField(description="Education level")
    end_year: SortableField = SortableField(description="End year")
    created_at: SortableField = SortableField(description="Creation date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["id:asc"]
