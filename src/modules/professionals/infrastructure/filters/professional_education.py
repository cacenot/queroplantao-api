"""
Filters and sorting for ProfessionalEducation entity.
"""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortingSet

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

    search: Annotated[
        str | None,
        Query(
            default=None,
            description="Search by course name or institution (partial, case-insensitive)",
        ),
    ] = None

    level: Annotated[
        EducationLevel | None,
        Query(
            default=None,
            description="Filter by education level",
        ),
    ] = None

    is_completed: Annotated[
        bool | None,
        Query(
            default=None,
            description="Filter by completion status",
        ),
    ] = None

    is_verified: Annotated[
        bool | None,
        Query(
            default=None,
            description="Filter by verification status",
        ),
    ] = None

    class Config:
        """FilterSet configuration."""

        search_fields = ["course_name", "institution"]
        field_columns = {
            "level": "level",
            "is_completed": "is_completed",
            "is_verified": "is_verified",
        }


class ProfessionalEducationSorting(SortingSet):
    """
    Sorting options for ProfessionalEducation.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by id (asc or desc). UUID v7 is time-ordered.",
        ),
    ] = None

    level: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by education level (asc or desc)",
        ),
    ] = None

    end_year: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by end year (asc or desc)",
        ),
    ] = None

    created_at: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by creation date (asc or desc)",
        ),
    ] = None

    class Config:
        """SortingSet configuration."""

        default_sort = [("id", "asc")]
        field_columns = {
            "id": "id",
            "level": "level",
            "end_year": "end_year",
            "created_at": "created_at",
        }
