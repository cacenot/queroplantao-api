"""
Filters and sorting for ProfessionalCompany entity.

Note: ProfessionalCompany is a junction table. Search by company_name
requires joining with Company table and is handled at repository level.
"""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortingSet


class ProfessionalCompanyFilter(FilterSet):
    """
    Filter for ProfessionalCompany queries.

    Note: Search by company_name is not available as it requires
    a join with the Company table.
    """

    # Note: Removed search as company_name is in related Company table

    class Config:
        """FilterSet configuration."""

        field_columns = {}


class ProfessionalCompanySorting(SortingSet):
    """
    Sorting options for ProfessionalCompany.

    Default sorting is by id (UUID v7 - time-ordered).
    Note: Sorting by company_name requires join and is not supported here.
    """

    id: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by id (asc or desc). UUID v7 is time-ordered.",
        ),
    ] = None

    joined_at: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by join date (asc or desc)",
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
            "joined_at": "joined_at",
            "created_at": "created_at",
        }
