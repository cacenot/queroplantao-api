"""Filters and sorting for screening module queries."""

from typing import Annotated

from fastapi import Query
from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.sortingset import SortableField, SortingSet

from src.modules.screening.domain.models.enums import ScreeningStatus


class ScreeningProcessFilter(FilterSet):
    """Filter options for screening processes."""

    search: Annotated[str | None, Query(default=None)] = None
    status: Annotated[ScreeningStatus | None, Query(default=None)] = None
    actor_id: Annotated[str | None, Query(default=None)] = None
    client_company_id: Annotated[str | None, Query(default=None)] = None
    is_active: Annotated[bool | None, Query(default=None)] = None

    class Config:
        """Filter configuration."""

        search_fields = ["professional_name", "professional_cpf"]
        field_columns = {
            "status": "status",
            "actor_id": "current_actor_id",
            "client_company_id": "client_company_id",
        }


class ScreeningProcessSorting(SortingSet):
    """Sorting options for screening processes."""

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    created_at: SortableField = SortableField(description="Creation date")
    updated_at: SortableField = SortableField(description="Last update date")
    status: SortableField = SortableField(description="Screening status")
    professional_name: SortableField = SortableField(description="Professional name")

    class Config:
        """Sorting configuration."""

        default_sorting = ["id:desc"]


class DocumentTypeConfigFilter(FilterSet):
    """Filter options for document type configurations."""

    search: Annotated[str | None, Query(default=None)] = None
    category: Annotated[str | None, Query(default=None)] = None
    is_active: Annotated[bool | None, Query(default=None)] = None

    class Config:
        """Filter configuration."""

        search_fields = ["name", "code", "help_text"]
        field_columns = {
            "category": "category",
            "is_active": "is_active",
        }


class DocumentTypeConfigSorting(SortingSet):
    """Sorting options for document type configurations."""

    id: SortableField = SortableField(description="ID (UUID v7 is time-ordered)")
    name: SortableField = SortableField(description="Document type name")
    display_order: SortableField = SortableField(description="Display order")

    class Config:
        """Sorting configuration."""

        default_sorting = ["display_order:asc", "name:asc"]
