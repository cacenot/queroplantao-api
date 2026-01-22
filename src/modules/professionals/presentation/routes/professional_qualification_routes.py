"""Professional Qualification routes (nested under professionals)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.modules.professionals.domain.schemas import (
    ProfessionalQualificationCreate,
    ProfessionalQualificationResponse,
    ProfessionalQualificationUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalQualificationFilter,
    ProfessionalQualificationSorting,
)
from src.modules.professionals.presentation.dependencies import (
    CreateProfessionalQualificationUC,
    DeleteProfessionalQualificationUC,
    GetProfessionalQualificationUC,
    ListProfessionalQualificationsUC,
    OrganizationContext,
    UpdateProfessionalQualificationUC,
)


# Nested under /professionals/{professional_id}
router = APIRouter(
    prefix="/{professional_id}/qualifications",
    tags=["Professional Qualifications"],
)


@router.post(
    "/",
    response_model=ProfessionalQualificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a qualification to a professional",
    description="Create a new qualification (e.g., CRM, COREN) for a professional.",
)
async def create_qualification(
    professional_id: UUID,
    data: ProfessionalQualificationCreate,
    ctx: OrganizationContext,
    use_case: CreateProfessionalQualificationUC,
) -> ProfessionalQualificationResponse:
    """Create a new qualification for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        created_by=ctx.user,
    )
    return ProfessionalQualificationResponse.model_validate(result)


@router.get(
    "/",
    response_model=PaginatedResponse[ProfessionalQualificationResponse],
    summary="List professional qualifications",
    description="List all qualifications for a professional with pagination, filtering and sorting.",
)
async def list_qualifications(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: ListProfessionalQualificationsUC,
    pagination: PaginationParams = Depends(),
    filters: ProfessionalQualificationFilter = Depends(
        filter_as_query(ProfessionalQualificationFilter)
    ),
    sorting: ProfessionalQualificationSorting = Depends(
        sorting_as_query(ProfessionalQualificationSorting)
    ),
) -> PaginatedResponse[ProfessionalQualificationResponse]:
    """List all qualifications for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result


@router.get(
    "/{qualification_id}",
    response_model=ProfessionalQualificationResponse,
    summary="Get a professional qualification",
    description="Get a specific qualification by ID.",
)
async def get_qualification(
    professional_id: UUID,
    qualification_id: UUID,
    ctx: OrganizationContext,
    use_case: GetProfessionalQualificationUC,
) -> ProfessionalQualificationResponse:
    """Get a qualification by ID."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        qualification_id=qualification_id,
    )
    return ProfessionalQualificationResponse.model_validate(result)


@router.patch(
    "/{qualification_id}",
    response_model=ProfessionalQualificationResponse,
    summary="Update a professional qualification",
    description="Partially update a qualification. Only provided fields will be updated.",
)
async def update_qualification(
    professional_id: UUID,
    qualification_id: UUID,
    data: ProfessionalQualificationUpdate,
    ctx: OrganizationContext,
    use_case: UpdateProfessionalQualificationUC,
) -> ProfessionalQualificationResponse:
    """Update a qualification."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        qualification_id=qualification_id,
        data=data,
        updated_by=ctx.user,
    )
    return ProfessionalQualificationResponse.model_validate(result)


@router.delete(
    "/{qualification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a professional qualification",
    description="Soft delete a qualification.",
)
async def delete_qualification(
    professional_id: UUID,
    qualification_id: UUID,
    ctx: OrganizationContext,
    use_case: DeleteProfessionalQualificationUC,
) -> None:
    """Soft delete a qualification."""
    await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        qualification_id=qualification_id,
        deleted_by=ctx.user,
    )
