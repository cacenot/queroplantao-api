"""Organization Professional routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.modules.professionals.domain.schemas import (
    OrganizationProfessionalCreate,
    OrganizationProfessionalListItem,
    OrganizationProfessionalResponse,
    OrganizationProfessionalUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    OrganizationProfessionalFilter,
    OrganizationProfessionalSorting,
)
from src.modules.professionals.presentation.dependencies import (
    CreateOrganizationProfessionalUC,
    DeleteOrganizationProfessionalUC,
    GetOrganizationProfessionalUC,
    ListOrganizationProfessionalsUC,
    ListOrganizationProfessionalsSummaryUC,
    OrganizationContext,
    UpdateOrganizationProfessionalUC,
)


# No prefix here - it's defined in the parent router (/professionals)
router = APIRouter(tags=["Professionals"])


@router.post(
    "/",
    response_model=OrganizationProfessionalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a professional",
    description="Create a new professional in the organization.",
)
async def create_professional(
    data: OrganizationProfessionalCreate,
    ctx: OrganizationContext,
    use_case: CreateOrganizationProfessionalUC,
) -> OrganizationProfessionalResponse:
    """Create a new professional in the organization."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        data=data,
        created_by=ctx.user,
    )
    return OrganizationProfessionalResponse.model_validate(result)


@router.get(
    "/",
    response_model=PaginatedResponse[OrganizationProfessionalResponse],
    summary="List professionals",
    description="List all professionals in the organization with pagination, filtering and sorting.",
)
async def list_professionals(
    ctx: OrganizationContext,
    use_case: ListOrganizationProfessionalsUC,
    pagination: PaginationParams = Depends(),
    filters: OrganizationProfessionalFilter = Depends(
        filter_as_query(OrganizationProfessionalFilter)
    ),
    sorting: OrganizationProfessionalSorting = Depends(
        sorting_as_query(OrganizationProfessionalSorting)
    ),
) -> PaginatedResponse[OrganizationProfessionalResponse]:
    """List all professionals in the organization."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result


@router.get(
    "/summary",
    response_model=PaginatedResponse[OrganizationProfessionalListItem],
    summary="List professionals (summary)",
    description="List professionals with simplified data: basic info, primary qualification, and specialties.",
)
async def list_professionals_summary(
    ctx: OrganizationContext,
    use_case: ListOrganizationProfessionalsSummaryUC,
    pagination: PaginationParams = Depends(),
    filters: OrganizationProfessionalFilter = Depends(
        filter_as_query(OrganizationProfessionalFilter)
    ),
    sorting: OrganizationProfessionalSorting = Depends(
        sorting_as_query(OrganizationProfessionalSorting)
    ),
) -> PaginatedResponse[OrganizationProfessionalListItem]:
    """List professionals with summary data."""
    return await use_case.execute(
        organization_id=ctx.organization,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )


@router.get(
    "/{professional_id}",
    response_model=OrganizationProfessionalResponse,
    summary="Get a professional",
    description="Get a professional by ID.",
)
async def get_professional(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: GetOrganizationProfessionalUC,
) -> OrganizationProfessionalResponse:
    """Get a professional by ID."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
    )
    return OrganizationProfessionalResponse.model_validate(result)


@router.patch(
    "/{professional_id}",
    response_model=OrganizationProfessionalResponse,
    summary="Update a professional",
    description="Partially update a professional. Only provided fields will be updated.",
)
async def update_professional(
    professional_id: UUID,
    data: OrganizationProfessionalUpdate,
    ctx: OrganizationContext,
    use_case: UpdateOrganizationProfessionalUC,
) -> OrganizationProfessionalResponse:
    """Update a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        updated_by=ctx.user,
    )
    return OrganizationProfessionalResponse.model_validate(result)


@router.delete(
    "/{professional_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a professional",
    description="Soft delete a professional. The professional will be marked as deleted but not removed from the database.",
)
async def delete_professional(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: DeleteOrganizationProfessionalUC,
) -> None:
    """Soft delete a professional."""
    await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        deleted_by=ctx.user,
    )
