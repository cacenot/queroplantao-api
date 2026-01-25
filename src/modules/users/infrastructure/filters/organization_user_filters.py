"""
Filters and sorting for OrganizationMembership (organization users) entity.
"""

from typing import Optional
from uuid import UUID

from pydantic import Field
from fastapi_restkit.filters import ListFilter, SearchFilter
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet


class OrganizationUserFilter(FilterSet):
    """
    Filter for organization user (membership) queries.

    Supports:
    - search: Full-text search across user's full_name and email
    - role_id: Filter by specific role
    - is_active: Filter by active/inactive status
    - is_pending: Filter by pending invitation status
    """

    search: Optional[SearchFilter] = Field(
        default=None,
        description="Search by user name or email (partial, case-insensitive)",
    )

    role_id: Optional[ListFilter[UUID]] = Field(
        default=None,
        description="Filter by role ID",
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="Filter by active status",
    )

    is_pending: Optional[bool] = Field(
        default=None,
        description="Filter by pending invitation status",
    )

    class Config:
        """FilterSet configuration."""

        field_columns = {
            "search": ["user.full_name", "user.email"],
            "role_id": "role_id",
            "is_active": "is_active",
        }


class OrganizationUserSorting(SortingSet):
    """
    Sorting options for organization users.

    Default sort: created_at descending (newest first).
    """

    id: Optional[SortableField] = Field(
        default=None,
        description="Sort by membership ID (UUID v7 = creation order)",
    )

    created_at: Optional[SortableField] = Field(
        default=None,
        description="Sort by creation date",
    )

    granted_at: Optional[SortableField] = Field(
        default=None,
        description="Sort by role grant date",
    )

    class Config:
        """SortingSet configuration."""

        default_sort = [("created_at", "desc")]

        field_columns = {
            "id": "id",
            "created_at": "created_at",
            "granted_at": "granted_at",
        }
