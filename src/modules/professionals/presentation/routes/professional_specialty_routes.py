"""Professional Specialty routes (nested under professionals)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.modules.professionals.domain.schemas import (
    ProfessionalSpecialtyCreate,
    ProfessionalSpecialtyResponse,
    ProfessionalSpecialtyUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalSpecialtyFilter,
    ProfessionalSpecialtySorting,
)
from src.modules.professionals.presentation.dependencies import (
    CreateProfessionalSpecialtyUC,
    DeleteProfessionalSpecialtyUC,
    GetProfessionalSpecialtyUC,
    ListProfessionalSpecialtiesUC,
    OrganizationContext,
    UpdateProfessionalSpecialtyUC,
)


# Nested under /professionals/{professional_id}
router = APIRouter(
    prefix="/{professional_id}/specialties",
    tags=["Professional Specialties"],
)


@router.post(
    "/",
    response_model=ProfessionalSpecialtyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a specialty to a professional",
    description="Link a specialty to a professional.",
)
async def create_specialty(
    professional_id: UUID,
    data: ProfessionalSpecialtyCreate,
    ctx: OrganizationContext,
    use_case: CreateProfessionalSpecialtyUC,
) -> ProfessionalSpecialtyResponse:
    """Link a specialty to a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        created_by=ctx.user,
        family_org_ids=ctx.family_org_ids,
    )
    return ProfessionalSpecialtyResponse.model_validate(result)


@router.get(
    "/",
    response_model=PaginatedResponse[ProfessionalSpecialtyResponse],
    summary="List professional specialties",
    description="List all specialties for a professional with pagination, filtering and sorting.",
)
async def list_specialties(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: ListProfessionalSpecialtiesUC,
    pagination: PaginationParams = Depends(),
    filters: ProfessionalSpecialtyFilter = Depends(
        filter_as_query(ProfessionalSpecialtyFilter)
    ),
    sorting: ProfessionalSpecialtySorting = Depends(
        sorting_as_query(ProfessionalSpecialtySorting)
    ),
) -> PaginatedResponse[ProfessionalSpecialtyResponse]:
    """List all specialties for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result


@router.get(
    "/{specialty_link_id}",
    response_model=ProfessionalSpecialtyResponse,
    summary="Get a professional specialty link",
    description="Get a specific specialty link by ID.",
)
async def get_specialty(
    professional_id: UUID,
    specialty_link_id: UUID,
    ctx: OrganizationContext,
    use_case: GetProfessionalSpecialtyUC,
) -> ProfessionalSpecialtyResponse:
    """Get a specialty link by ID."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        specialty_link_id=specialty_link_id,
    )
    return ProfessionalSpecialtyResponse.model_validate(result)


@router.patch(
    "/{specialty_link_id}",
    response_model=ProfessionalSpecialtyResponse,
    summary="Update a professional specialty link",
    description="Partially update a specialty link. Only provided fields will be updated.",
)
async def update_specialty(
    professional_id: UUID,
    specialty_link_id: UUID,
    data: ProfessionalSpecialtyUpdate,
    ctx: OrganizationContext,
    use_case: UpdateProfessionalSpecialtyUC,
) -> ProfessionalSpecialtyResponse:
    """Update a specialty link."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        specialty_link_id=specialty_link_id,
        data=data,
        updated_by=ctx.user,
    )
    return ProfessionalSpecialtyResponse.model_validate(result)


@router.delete(
    "/{specialty_link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a specialty from a professional",
    description="Soft delete a specialty link.",
)
async def delete_specialty(
    professional_id: UUID,
    specialty_link_id: UUID,
    ctx: OrganizationContext,
    use_case: DeleteProfessionalSpecialtyUC,
) -> None:
    """Soft delete a specialty link."""
    await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        specialty_link_id=specialty_link_id,
        deleted_by=ctx.user,
    )
