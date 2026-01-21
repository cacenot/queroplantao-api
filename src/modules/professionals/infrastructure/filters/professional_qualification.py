"""
Filters and sorting for ProfessionalQualification entity.
"""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filters import FilterSet
from fastapi_restkit.sorting import SortingSet

from src.modules.professionals.domain.models import CouncilType, ProfessionalType


class ProfessionalQualificationFilter(FilterSet):
    """
    Filter for ProfessionalQualification queries.

    Supports:
    - search: Search across council_number
    - professional_type: Filter by professional type (DOCTOR, NURSE, etc.)
    - council_type: Filter by council type (CRM, COREN, etc.)
    - council_state: Filter by council state (UF)
    - is_primary: Filter by primary qualification flag
    - is_verified: Filter by verification status
    """

    search: Annotated[
        str | None,
        Query(
            default=None,
            description="Search by council number (partial, case-insensitive)",
        ),
    ] = None

    professional_type: Annotated[
        ProfessionalType | None,
        Query(
            default=None,
            description="Filter by professional type (DOCTOR, NURSE, etc.)",
        ),
    ] = None

    council_type: Annotated[
        CouncilType | None,
        Query(
            default=None,
            description="Filter by council type (CRM, COREN, etc.)",
        ),
    ] = None

    council_state: Annotated[
        str | None,
        Query(
            default=None,
            max_length=2,
            description="Filter by council state (2-char UF)",
        ),
    ] = None

    is_primary: Annotated[
        bool | None,
        Query(
            default=None,
            description="Filter by primary qualification flag",
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

        search_fields = ["council_number"]
        field_columns = {
            "professional_type": "professional_type",
            "council_type": "council_type",
            "council_state": "council_state",
            "is_primary": "is_primary",
            "is_verified": "is_verified",
        }


class ProfessionalQualificationSorting(SortingSet):
    """
    Sorting options for ProfessionalQualification.

    Default sorting is by id (UUID v7 - time-ordered).
    """

    id: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by id (asc or desc). UUID v7 is time-ordered.",
        ),
    ] = None

    professional_type: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by professional type (asc or desc)",
        ),
    ] = None

    council_state: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by council state (asc or desc)",
        ),
    ] = None

    graduation_year: Annotated[
        str | None,
        Query(
            default=None,
            description="Sort by graduation year (asc or desc)",
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
            "professional_type": "professional_type",
            "council_state": "council_state",
            "graduation_year": "graduation_year",
            "created_at": "created_at",
        }
