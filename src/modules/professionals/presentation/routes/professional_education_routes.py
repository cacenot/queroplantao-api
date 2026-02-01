"""Professional Education routes (nested under professionals)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.modules.professionals.domain.schemas import (
    ProfessionalEducationCreate,
    ProfessionalEducationResponse,
    ProfessionalEducationUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalEducationFilter,
    ProfessionalEducationSorting,
)
from src.modules.professionals.presentation.dependencies import (
    CreateProfessionalEducationUC,
    DeleteProfessionalEducationUC,
    GetProfessionalEducationUC,
    ListProfessionalEducationsUC,
    OrganizationContext,
    UpdateProfessionalEducationUC,
)


# Nested under /professionals/{professional_id}
router = APIRouter(
    prefix="/{professional_id}/educations",
    tags=["Professional Educations"],
)


@router.post(
    "/",
    response_model=ProfessionalEducationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an education to a professional",
    description="Create a new education record for a professional.",
)
async def create_education(
    professional_id: UUID,
    data: ProfessionalEducationCreate,
    ctx: OrganizationContext,
    use_case: CreateProfessionalEducationUC,
) -> ProfessionalEducationResponse:
    """Create a new education record for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        created_by=ctx.user,
        family_org_ids=ctx.family_org_ids,
    )
    return ProfessionalEducationResponse.model_validate(result)


@router.get(
    "/",
    response_model=PaginatedResponse[ProfessionalEducationResponse],
    summary="List professional educations",
    description="List all education records for a professional with pagination, filtering and sorting.",
)
async def list_educations(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: ListProfessionalEducationsUC,
    pagination: PaginationParams = Depends(),
    filters: ProfessionalEducationFilter = Depends(
        filter_as_query(ProfessionalEducationFilter)
    ),
    sorting: ProfessionalEducationSorting = Depends(
        sorting_as_query(ProfessionalEducationSorting)
    ),
) -> PaginatedResponse[ProfessionalEducationResponse]:
    """List all education records for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result


@router.get(
    "/{education_id}",
    response_model=ProfessionalEducationResponse,
    summary="Get a professional education",
    description="Get a specific education record by ID.",
)
async def get_education(
    professional_id: UUID,
    education_id: UUID,
    ctx: OrganizationContext,
    use_case: GetProfessionalEducationUC,
) -> ProfessionalEducationResponse:
    """Get an education record by ID."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        education_id=education_id,
    )
    return ProfessionalEducationResponse.model_validate(result)


@router.patch(
    "/{education_id}",
    response_model=ProfessionalEducationResponse,
    summary="Update a professional education",
    description="Partially update an education record. Only provided fields will be updated.",
)
async def update_education(
    professional_id: UUID,
    education_id: UUID,
    data: ProfessionalEducationUpdate,
    ctx: OrganizationContext,
    use_case: UpdateProfessionalEducationUC,
) -> ProfessionalEducationResponse:
    """Update an education record."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        education_id=education_id,
        data=data,
        updated_by=ctx.user,
    )
    return ProfessionalEducationResponse.model_validate(result)


@router.delete(
    "/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a professional education",
    description="Soft delete an education record.",
)
async def delete_education(
    professional_id: UUID,
    education_id: UUID,
    ctx: OrganizationContext,
    use_case: DeleteProfessionalEducationUC,
) -> None:
    """Soft delete an education record."""
    await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        education_id=education_id,
        deleted_by=ctx.user,
    )
