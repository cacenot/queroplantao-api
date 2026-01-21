"""
Filters and sorting for ProfessionalDocument entity.
"""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filters import FilterSet
from fastapi_restkit.sorting import SortingSet

from src.modules.professionals.domain.models import DocumentCategory, DocumentType


class ProfessionalDocumentFilter(FilterSet):
    """
    Filter for ProfessionalDocument queries.

    Supports:
    - search: Search across file_name
    - document_type: Filter by document type (ID_DOCUMENT, DIPLOMA, etc.)
    - document_category: Filter by category (PROFILE, QUALIFICATION, SPECIALTY)
    - is_verified: Filter by verification status
    """

    search: Annotated[
        str | None,
        Query(
            default=None,
            description="Search by file name (partial, case-insensitive)",
        ),
    ] = None

    document_type: Annotated[
        DocumentType | None,
        Query(
            default=None,
            description="Filter by document type",
        ),
    ] = None

    document_category: Annotated[
        DocumentCategory | None,
        Query(
            default=None,
            description="Filter by document category",
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

        search_fields = ["file_name"]
        field_columns = {
            "document_type": "document_type",
            "document_category": "document_category",
            "is_verified": "is_verified",
        }


class ProfessionalDocumentSorting(SortingSet):
    """
    Sorting options for ProfessionalDocument.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by id (asc or desc). UUID v7 is time-ordered.",
        ),
    ] = None

    document_type: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by document type (asc or desc)",
        ),
    ] = None

    file_name: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by file name (asc or desc)",
        ),
    ] = None

    expires_at: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by expiration date (asc or desc)",
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
            "document_type": "document_type",
            "file_name": "file_name",
            "expires_at": "expires_at",
            "created_at": "created_at",
        }
