"""
Filters and sorting for ProfessionalCompany entity.

Note: ProfessionalCompany is a junction table. Search by company_name
requires joining with Company table and is handled at repository level.
"""

from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet


class ProfessionalCompanyFilter(FilterSet):
    """
    Filter for ProfessionalCompany queries.

    Note: Search by company_name is not available as it requires
    a join with the Company table.
    """

    class Config:
        """FilterSet configuration."""

        field_columns = {}


class ProfessionalCompanySorting(SortingSet):
    """
    Sorting options for ProfessionalCompany.

    Default sorting is by id (UUID v7 - time-ordered).
    Note: Sorting by company_name requires join and is not supported here.
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    joined_at: SortableField = SortableField(description="Join date")
    created_at: SortableField = SortableField(description="Creation date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["id:asc"]
