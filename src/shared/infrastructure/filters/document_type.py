"""
Filters and sorting for DocumentType entity.
"""

from typing import Optional

from pydantic import Field
from fastapi_restkit.filters import SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet

from src.shared.domain.models import DocumentCategory
from src.shared.infrastructure.filters.base import ExcludeListFilter


class DocumentTypeFilter(FilterSet):
    """
    Filter for DocumentType queries.

    Supports:
    - search: Search by name (using pg_trgm for fuzzy matching)
    - category: Filter by document category (include)
    - exclude_categories: Exclude specific categories (NOT IN)
    - is_active: Filter by active status
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by name (partial, case-insensitive, accent-insensitive)",
    )
    category: Optional[DocumentCategory] = Field(
        default=None,
        description="Filter by document category (PROFILE, QUALIFICATION, SPECIALTY)",
    )
    exclude_categories: Optional[ExcludeListFilter[DocumentCategory]] = Field(
        default=None,
        description="Exclude specific categories (NOT IN clause)",
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Filter by active status",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["name"],
            "category": "category",
            "exclude_categories": "category",
            "is_active": "is_active",
        }


class DocumentTypeSorting(SortingSet):
    """
    Sorting options for DocumentType.

    Default sorting is by display_order then name alphabetically.
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    name: SortableField = SortableField(description="Document type name")
    display_order: SortableField = SortableField(description="Display order")
    created_at: SortableField = SortableField(description="Creation date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["display_order:asc", "name:asc"]
