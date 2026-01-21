"""
Filters and sorting for ProfessionalSpecialty entity.
"""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortingSet


class ProfessionalSpecialtyFilter(FilterSet):
    """
    Filter for ProfessionalSpecialty queries.

    Supports:
    - search: Search across RQE number
    - is_verified: Filter by verification status
    """

    search: Annotated[
        str | None,
        Query(
            default=None,
            description="Search by RQE number (partial, case-insensitive)",
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

        search_fields = ["rqe_number"]
        field_columns = {
            "is_verified": "is_verified",
        }


class ProfessionalSpecialtySorting(SortingSet):
    """
    Sorting options for ProfessionalSpecialty.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by id (asc or desc). UUID v7 is time-ordered.",
        ),
    ] = None

    acquisition_date: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by acquisition date (asc or desc)",
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
            "acquisition_date": "acquisition_date",
            "created_at": "created_at",
        }
