"""Specialty routes (global, read-only reference data)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.shared.domain.schemas.specialty import (
    SpecialtyListResponse,
    SpecialtyResponse,
)
from src.shared.infrastructure.filters.specialty import (
    SpecialtyFilter,
    SpecialtySorting,
)
from src.shared.presentation.dependencies import (
    CurrentContext,
    GetSpecialtyByCodeUC,
    GetSpecialtyUC,
    ListSpecialtiesUC,
    SearchSpecialtiesUC,
)


router = APIRouter(prefix="/specialties", tags=["Specialties"])


@router.get(
    "/",
    response_model=PaginatedResponse[SpecialtyListResponse],
    summary="List specialties",
    description="List all medical specialties with pagination, filtering and sorting. This is global reference data.",
)
async def list_specialties(
    _context: CurrentContext,  # Require authentication but not organization
    use_case: ListSpecialtiesUC,
    pagination: PaginationParams = Depends(),
    filters: SpecialtyFilter = Depends(filter_as_query(SpecialtyFilter)),
    sorting: SpecialtySorting = Depends(sorting_as_query(SpecialtySorting)),
) -> PaginatedResponse[SpecialtyListResponse]:
    """List all medical specialties."""
    result = await use_case.execute(
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result


@router.get(
    "/search",
    response_model=PaginatedResponse[SpecialtyListResponse],
    summary="Search specialties",
    description="Search specialties by name or code using fuzzy matching.",
)
async def search_specialties(
    _context: CurrentContext,  # Require authentication but not organization
    use_case: SearchSpecialtiesUC,
    q: str = Query(..., min_length=2, description="Search query (min 2 characters)"),
    pagination: PaginationParams = Depends(),
    sorting: SpecialtySorting = Depends(sorting_as_query(SpecialtySorting)),
) -> PaginatedResponse[SpecialtyListResponse]:
    """Search specialties by name or code."""
    result = await use_case.execute(
        name=q,
        pagination=pagination,
        sorting=sorting,
    )
    return result


@router.get(
    "/code/{code}",
    response_model=SpecialtyResponse,
    summary="Get specialty by code",
    description="Get a specialty by its unique code (e.g., 'CARDIOLOGY').",
)
async def get_specialty_by_code(
    code: str,
    _context: CurrentContext,  # Require authentication but not organization
    use_case: GetSpecialtyByCodeUC,
) -> SpecialtyResponse:
    """Get a specialty by code."""
    result = await use_case.execute(code=code)
    return SpecialtyResponse.model_validate(result)


@router.get(
    "/{specialty_id}",
    response_model=SpecialtyResponse,
    summary="Get specialty",
    description="Get a specialty by ID.",
)
async def get_specialty(
    specialty_id: UUID,
    _context: CurrentContext,  # Require authentication but not organization
    use_case: GetSpecialtyUC,
) -> SpecialtyResponse:
    """Get a specialty by ID."""
    result = await use_case.execute(specialty_id=specialty_id)
    return SpecialtyResponse.model_validate(result)
