"""
Filters and sorting for ProfessionalVersion entity.
"""

from typing import Optional

from pydantic import Field
from fastapi_restkit.filters import BooleanFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet


class ProfessionalVersionFilter(FilterSet):
    """
    Filter for ProfessionalVersion queries.

    Supports:
    - is_current: Filter by current status
    - is_pending: Filter by pending status (not applied, not rejected)
    - source_type: Filter by source type
    """

    is_current: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by current version status",
    )

    is_applied: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by applied status (has applied_at)",
    )

    is_rejected: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by rejected status (has rejected_at)",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {}


class ProfessionalVersionSorting(SortingSet):
    """
    Sorting options for ProfessionalVersion.

    Default sorting is by version_number descending (newest first).
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    version_number: SortableField = SortableField(description="Version number")
    created_at: SortableField = SortableField(description="Creation date")
    applied_at: SortableField = SortableField(description="Application date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["version_number:desc"]
