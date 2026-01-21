"""
Filters and sorting for Specialty entity (global reference data).
"""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortingSet


class SpecialtyFilter(FilterSet):
    """
    Filter for Specialty queries.

    Supports:
    - search: Search across code, name (using pg_trgm for fuzzy matching)
    """

    search: Annotated[
        str | None,
        Query(
            default=None,
            description="Search by code or name (partial, case-insensitive, accent-insensitive)",
        ),
    ] = None

    class Config:
        """FilterSet configuration."""

        search_fields = ["code", "name"]


class SpecialtySorting(SortingSet):
    """
    Sorting options for Specialty.

    Default sorting is by name alphabetically.
    """

    id: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by id (asc or desc). UUID v7 is time-ordered.",
        ),
    ] = None

    code: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by code (asc or desc)",
        ),
    ] = None

    name: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by name (asc or desc)",
        ),
    ] = None

    class Config:
        """SortingSet configuration."""

        default_sort = [("name", "asc")]
        field_columns = {
            "id": "id",
            "code": "code",
            "name": "name",
        }
