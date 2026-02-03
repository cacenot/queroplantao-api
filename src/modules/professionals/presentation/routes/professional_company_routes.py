"""Professional Company routes (nested under professionals)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.modules.professionals.domain.schemas import (
    ProfessionalCompanyCreate,
    ProfessionalCompanyResponse,
    ProfessionalCompanyUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalCompanyFilter,
    ProfessionalCompanySorting,
)
from src.modules.professionals.presentation.dependencies import (
    CreateProfessionalCompanyUC,
    DeleteProfessionalCompanyUC,
    GetProfessionalCompanyUC,
    ListProfessionalCompaniesUC,
    OrganizationContext,
    UpdateProfessionalCompanyUC,
)


# Nested under /professionals/{professional_id}
router = APIRouter(
    prefix="/{professional_id}/companies",
    tags=["Professional Companies"],
)


@router.post(
    "/",
    response_model=ProfessionalCompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link a company to a professional",
    description="Create a link between a professional and a company (PJ relationship).",
)
async def create_company_link(
    professional_id: UUID,
    data: ProfessionalCompanyCreate,
    ctx: OrganizationContext,
    use_case: CreateProfessionalCompanyUC,
) -> ProfessionalCompanyResponse:
    """Create a link between a professional and a company."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        created_by=ctx.user,
    )
    return ProfessionalCompanyResponse.model_validate(result)


@router.get(
    "/",
    response_model=PaginatedResponse[ProfessionalCompanyResponse],
    summary="List professional companies",
    description="List all company links for a professional with pagination, filtering and sorting.",
)
async def list_company_links(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: ListProfessionalCompaniesUC,
    pagination: PaginationParams = Depends(),
    filters: ProfessionalCompanyFilter = Depends(
        filter_as_query(ProfessionalCompanyFilter)
    ),
    sorting: ProfessionalCompanySorting = Depends(
        sorting_as_query(ProfessionalCompanySorting)
    ),
) -> PaginatedResponse[ProfessionalCompanyResponse]:
    """List all company links for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result


@router.get(
    "/{company_link_id}",
    response_model=ProfessionalCompanyResponse,
    summary="Get a professional company link",
    description="Get a specific company link by ID.",
)
async def get_company_link(
    professional_id: UUID,
    company_link_id: UUID,
    ctx: OrganizationContext,
    use_case: GetProfessionalCompanyUC,
) -> ProfessionalCompanyResponse:
    """Get a company link by ID."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        company_link_id=company_link_id,
    )
    return ProfessionalCompanyResponse.model_validate(result)


@router.patch(
    "/{company_link_id}",
    response_model=ProfessionalCompanyResponse,
    summary="Update a professional company link",
    description="Partially update a company link (e.g., update left_at date).",
)
async def update_company_link(
    professional_id: UUID,
    company_link_id: UUID,
    data: ProfessionalCompanyUpdate,
    ctx: OrganizationContext,
    use_case: UpdateProfessionalCompanyUC,
) -> ProfessionalCompanyResponse:
    """Update a company link."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        company_link_id=company_link_id,
        data=data,
        updated_by=ctx.user,
    )
    return ProfessionalCompanyResponse.model_validate(result)


@router.delete(
    "/{company_link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a company link from a professional",
    description="Soft delete a company link.",
)
async def delete_company_link(
    professional_id: UUID,
    company_link_id: UUID,
    ctx: OrganizationContext,
    use_case: DeleteProfessionalCompanyUC,
) -> None:
    """Soft delete a company link."""
    await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        company_link_id=company_link_id,
        deleted_by=ctx.user,
    )
