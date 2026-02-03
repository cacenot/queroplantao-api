"""Organization Professional routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.app.constants.error_codes import ProfessionalErrorCodes
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
from src.shared.domain.schemas.common import ErrorResponse


# No prefix here - it's defined in the parent router (/professionals)
router = APIRouter(tags=["Professionals"])


@router.post(
    "/",
    response_model=OrganizationProfessionalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a professional",
    description="Create a new professional in the organization.",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Conflict - CPF or email already exists",
            "content": {
                "application/json": {
                    "examples": {
                        "cpf_exists": {
                            "summary": "CPF already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.CPF_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este CPF na organização",
                            },
                        },
                        "email_exists": {
                            "summary": "Email already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.EMAIL_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este email na organização",
                            },
                        },
                    }
                }
            },
        },
    },
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
        family_org_ids=ctx.family_org_ids,
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
        family_org_ids=ctx.family_org_ids,
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
        family_org_ids=ctx.family_org_ids,
    )


@router.get(
    "/{professional_id}",
    response_model=OrganizationProfessionalDetailResponse,
    summary="Get a professional",
    description="Get a professional by ID with all related data: qualifications, specialties, educations, documents, companies, and bank accounts.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Professional not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": ProfessionalErrorCodes.PROFESSIONAL_NOT_FOUND,
                        "message": "Profissional não encontrado",
                    }
                }
            },
        },
    },
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
        family_org_ids=ctx.family_org_ids,
    )
    return OrganizationProfessionalDetailResponse.from_model(result)


@router.patch(
    "/{professional_id}",
    response_model=OrganizationProfessionalResponse,
    summary="Update a professional",
    description="Partially update a professional. Only provided fields will be updated.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Professional not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": ProfessionalErrorCodes.PROFESSIONAL_NOT_FOUND,
                        "message": "Profissional não encontrado",
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict - CPF or email already exists",
            "content": {
                "application/json": {
                    "examples": {
                        "cpf_exists": {
                            "summary": "CPF already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.CPF_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este CPF na organização",
                            },
                        },
                        "email_exists": {
                            "summary": "Email already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.EMAIL_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este email na organização",
                            },
                        },
                    }
                }
            },
        },
    },
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
        family_org_ids=ctx.family_org_ids,
    )
    return OrganizationProfessionalResponse.model_validate(result)


@router.delete(
    "/{professional_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a professional",
    description="Soft delete a professional. The professional will be marked as deleted but not removed from the database.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Professional not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": ProfessionalErrorCodes.PROFESSIONAL_NOT_FOUND,
                        "message": "Profissional não encontrado",
                    }
                }
            },
        },
    },
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
        family_org_ids=ctx.family_org_ids,
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
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Specialty not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": ProfessionalErrorCodes.GLOBAL_SPECIALTY_NOT_FOUND,
                        "message": "Especialidade não encontrada",
                        "details": {"specialty_id": "019..."},
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict - CPF, email, or council registration already exists",
            "content": {
                "application/json": {
                    "examples": {
                        "cpf_exists": {
                            "summary": "CPF already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.CPF_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este CPF na organização",
                            },
                        },
                        "email_exists": {
                            "summary": "Email already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.EMAIL_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este email na organização",
                            },
                        },
                        "council_exists": {
                            "summary": "Council registration already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.COUNCIL_REGISTRATION_EXISTS,
                                "message": "Já existe um profissional com este registro de conselho na organização",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "code": ProfessionalErrorCodes.DUPLICATE_SPECIALTY_IDS,
                        "message": "IDs de especialidade duplicados na requisição",
                    }
                }
            },
        },
    },
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
        family_org_ids=ctx.family_org_ids,
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
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "examples": {
                        "professional_not_found": {
                            "summary": "Professional not found",
                            "value": {
                                "code": ProfessionalErrorCodes.PROFESSIONAL_NOT_FOUND,
                                "message": "Profissional não encontrado",
                            },
                        },
                        "specialty_not_found": {
                            "summary": "Specialty not found",
                            "value": {
                                "code": ProfessionalErrorCodes.GLOBAL_SPECIALTY_NOT_FOUND,
                                "message": "Especialidade não encontrada",
                                "details": {"specialty_id": "019..."},
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict - CPF, email, council registration, or specialty already exists",
            "content": {
                "application/json": {
                    "examples": {
                        "cpf_exists": {
                            "summary": "CPF already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.CPF_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este CPF na organização",
                            },
                        },
                        "email_exists": {
                            "summary": "Email already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.EMAIL_ALREADY_EXISTS,
                                "message": "Já existe um profissional com este email na organização",
                            },
                        },
                        "council_exists": {
                            "summary": "Council registration already exists",
                            "value": {
                                "code": ProfessionalErrorCodes.COUNCIL_REGISTRATION_EXISTS,
                                "message": "Já existe um profissional com este registro de conselho na organização",
                            },
                        },
                        "specialty_assigned": {
                            "summary": "Specialty already assigned",
                            "value": {
                                "code": ProfessionalErrorCodes.SPECIALTY_ALREADY_ASSIGNED,
                                "message": "Esta especialidade já está atribuída à qualificação",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_specialty_ids": {
                            "summary": "Duplicate specialty IDs",
                            "value": {
                                "code": ProfessionalErrorCodes.DUPLICATE_SPECIALTY_IDS,
                                "message": "IDs de especialidade duplicados na requisição",
                            },
                        },
                        "qualification_id_required": {
                            "summary": "Qualification ID required",
                            "value": {
                                "code": ProfessionalErrorCodes.QUALIFICATION_ID_REQUIRED,
                                "message": "ID da qualificação é obrigatório",
                            },
                        },
                    }
                }
            },
        },
    },
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
        family_org_ids=ctx.family_org_ids,
    )
    return OrganizationProfessionalDetailResponse.from_model(result)
