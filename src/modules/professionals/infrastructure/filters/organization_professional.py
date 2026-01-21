"""
Filters and sorting for OrganizationProfessional entity.
"""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortingSet

from src.modules.professionals.domain.models import Gender, MaritalStatus


class OrganizationProfessionalFilter(FilterSet):
    """
    Filter for OrganizationProfessional queries.

    Supports:
    - search: Full-text search across full_name, email, cpf (using pg_trgm)
    - is_active: Filter by active status
    - gender: Filter by gender
    - marital_status: Filter by marital status
    """

    search: Annotated[
        str | None,
        Query(
            default=None,
            description="Search by name, email or CPF (partial, case-insensitive)",
        ),
    ] = None

    is_active: Annotated[
        bool | None,
        Query(
            default=None,
            description="Filter by active status",
        ),
    ] = None

    gender: Annotated[
        Gender | None,
        Query(
            default=None,
            description="Filter by gender (MALE, FEMALE)",
        ),
    ] = None

    marital_status: Annotated[
        MaritalStatus | None,
        Query(
            default=None,
            description="Filter by marital status",
        ),
    ] = None

    class Config:
        """FilterSet configuration."""

        # Map filter fields to model columns
        # "search" uses OR across multiple columns with ILIKE
        search_fields = ["full_name", "email", "cpf"]
        field_columns = {
            "is_active": "is_active",
            "gender": "gender",
            "marital_status": "marital_status",
        }


class OrganizationProfessionalSorting(SortingSet):
    """
    Sorting options for OrganizationProfessional.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by id (asc or desc). UUID v7 is time-ordered.",
        ),
    ] = None

    full_name: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by full name (asc or desc)",
        ),
    ] = None

    email: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by email (asc or desc)",
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

        # Default sort when no sorting is specified
        default_sort = [("id", "asc")]
        # Map sorting fields to model columns
        field_columns = {
            "id": "id",
            "full_name": "full_name",
            "email": "email",
            "created_at": "created_at",
        }
