"""Organization Professional routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.modules.professionals.domain.schemas import (
    OrganizationProfessionalCompositeCreate,
    OrganizationProfessionalCompositeUpdate,
    OrganizationProfessionalCreate,
    OrganizationProfessionalDetailResponse,
    OrganizationProfessionalListItem,
    OrganizationProfessionalResponse,
    OrganizationProfessionalUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    OrganizationProfessionalFilter,
    OrganizationProfessionalSorting,
)
from src.modules.professionals.presentation.dependencies import (
    CreateOrganizationProfessionalCompositeUC,
    CreateOrganizationProfessionalUC,
    DeleteOrganizationProfessionalUC,
    GetOrganizationProfessionalUC,
    ListOrganizationProfessionalsUC,
    ListOrganizationProfessionalsSummaryUC,
    OrganizationContext,
    UpdateOrganizationProfessionalCompositeUC,
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
    response_model=OrganizationProfessionalDetailResponse,
    summary="Get a professional",
    description="Get a professional by ID with all related data: qualifications, specialties, educations, documents, companies, and bank accounts.",
)
async def get_professional(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: GetOrganizationProfessionalUC,
) -> OrganizationProfessionalDetailResponse:
    """Get a professional by ID with all nested data."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        include_relations=True,
    )
    return OrganizationProfessionalDetailResponse.from_model(result)


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


# =============================================================================
# Composite endpoints (professional + qualification + specialties + educations)
# =============================================================================


@router.post(
    "/composite",
    response_model=OrganizationProfessionalDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a professional with qualification",
    description="""
Create a professional with one qualification and nested specialties and educations in a single transaction.

This endpoint creates:
- The professional (basic info + address)
- One qualification (council registration)
- Specialties for the qualification (optional)
- Educations for the qualification (optional)

All entities are created atomically - if any validation fails, nothing is persisted.

**Validations:**
- CPF uniqueness within the organization
- Email uniqueness within the organization  
- Council registration uniqueness within the organization
- All specialty_ids must exist in the global specialties table
- No duplicate specialty_ids in the request
""",
)
async def create_professional_composite(
    data: OrganizationProfessionalCompositeCreate,
    ctx: OrganizationContext,
    use_case: CreateOrganizationProfessionalCompositeUC,
) -> OrganizationProfessionalDetailResponse:
    """Create a professional with qualification, specialties, and educations."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        data=data,
        created_by=ctx.user,
    )
    return OrganizationProfessionalDetailResponse.from_model(result)


@router.patch(
    "/{professional_id}/composite",
    response_model=OrganizationProfessionalDetailResponse,
    summary="Update a professional with qualification",
    description="""
Partially update a professional with qualification and nested entities.

**Professional fields:** PATCH semantics - only update provided fields.

**Qualification:** Must provide the qualification ID. Updates only provided fields.

**Specialties/Educations partial update strategy:**
- **With ID + other fields:** Update existing entity
- **With ID only:** Keep unchanged (no fields to update)
- **Without ID:** Create new entity (specialty_id required for specialties)
- **Existing IDs not in list:** Soft delete
- **null list:** No changes to that entity type
- **Empty list []:** Remove all entities of that type

**Validations:**
- CPF/email uniqueness (excluding current professional)
- Council registration uniqueness (if updating)
- Specialty_id existence and no duplicates
""",
)
async def update_professional_composite(
    professional_id: UUID,
    data: OrganizationProfessionalCompositeUpdate,
    ctx: OrganizationContext,
    use_case: UpdateOrganizationProfessionalCompositeUC,
) -> OrganizationProfessionalDetailResponse:
    """Update a professional with qualification, specialties, and educations."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        updated_by=ctx.user,
    )
    return OrganizationProfessionalDetailResponse.from_model(result)
