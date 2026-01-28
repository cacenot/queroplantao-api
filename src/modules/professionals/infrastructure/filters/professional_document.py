"""
Filters and sorting for ProfessionalDocument entity.
"""

from typing import Optional
from uuid import UUID

from pydantic import Field
from fastapi_restkit.filters import BooleanFilter, ListFilter, SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet

from src.shared.domain.models import DocumentCategory


class ProfessionalDocumentFilter(FilterSet):
    """
    Filter for ProfessionalDocument queries.

    Supports:
    - search: Search across file_name
    - document_type_id: Filter by document type ID (UUID)
    - document_category: Filter by category (PROFILE, QUALIFICATION, SPECIALTY)
    - is_verified: Filter by verification status
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by file name (partial, case-insensitive)",
    )

    document_type_id: Optional[ListFilter[UUID]] = Field(
        default=None,
        description="Filter by document type ID",
    )

    document_category: Optional[ListFilter[DocumentCategory]] = Field(
        default=None,
        description="Filter by document category",
    )

    is_verified: Optional[BooleanFilter] = Field(
        default=None,
        description="Filter by verification status",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["file_name"],
        }


class ProfessionalDocumentSorting(SortingSet):
    """
    Sorting options for ProfessionalDocument.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    document_type: SortableField = SortableField(description="Document type")
    file_name: SortableField = SortableField(description="File name")
    expires_at: SortableField = SortableField(description="Expiration date")
    created_at: SortableField = SortableField(description="Creation date")

    class Config:
        """SortingSet configuration."""

        default_sorting = ["id:asc"]
