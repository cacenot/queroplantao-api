"""
Filters and sorting for ProfessionalCompany entity.

Note: ProfessionalCompany is a junction table. Search by company_name
requires joining with Company table and is handled at repository level.
"""

from typing import Optional
from uuid import UUID

from pydantic import Field
from fastapi_restkit.filters import BooleanFilter, ListFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet


class ProfessionalCompanyFilter(FilterSet):
    """
    Filter for ProfessionalCompany queries.

    Note: Search by company_name is not available as it requires
    a join with the Company table.
    """

    organization_professional_id: Optional[ListFilter[UUID]] = Field(
        default=None,
        description="Filter by organization professional ID",
    )

    is_active: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by active status (left_at is null)",
    )

    def to_sqlalchemy(self, model_class, use_or: bool = False):
        conditions = super().to_sqlalchemy(model_class, use_or=use_or) or []

        if self.is_active and self.is_active.value is not None:
            is_active = self.is_active.value
            condition = (
                model_class.left_at.is_(None)
                if is_active
                else model_class.left_at.is_not(None)
            )
            conditions.append(condition)

        return conditions

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
