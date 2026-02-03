"""Professional Version routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.app.constants.error_codes import ProfessionalErrorCodes
from src.modules.professionals.domain.schemas import (
    ProfessionalVersionCreate,
    ProfessionalVersionDetailResponse,
    ProfessionalVersionListResponse,
    ProfessionalVersionReject,
    ProfessionalVersionResponse,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalVersionFilter,
    ProfessionalVersionSorting,
)
from src.modules.professionals.presentation.dependencies import (
    OrganizationContext,
)
from src.modules.professionals.presentation.dependencies.professional_version import (
    ApplyProfessionalVersionUC,
    CreateProfessionalVersionUC,
    GetProfessionalVersionUC,
    ListProfessionalVersionsUC,
    RejectProfessionalVersionUC,
)
from src.shared.domain.schemas.common import ErrorResponse


router = APIRouter(tags=["Professional Versions"])


@router.post(
    "/{professional_id}/versions",
    response_model=ProfessionalVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a professional version",
    description=(
        "Create a new version for a professional. For DIRECT source type, "
        "the version is applied immediately. For SCREENING or other sources, "
        "the version remains pending until explicitly applied."
    ),
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Professional not found",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Professional not found",
                            "value": {
                                "code": ProfessionalErrorCodes.PROFESSIONAL_NOT_FOUND,
                                "message": "Profissional não encontrado",
                            },
                        },
                        "bank_not_found": {
                            "summary": "Bank not found",
                            "value": {
                                "code": ProfessionalErrorCodes.BANK_NOT_FOUND,
                                "message": "Banco não encontrado",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict - CPF or email already exists in family",
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
async def create_professional_version(
    professional_id: UUID,
    data: ProfessionalVersionCreate,
    ctx: OrganizationContext,
    use_case: CreateProfessionalVersionUC,
) -> ProfessionalVersionResponse:
    """Create a new version for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        family_org_ids=ctx.family_org_ids,
        created_by=ctx.user,
    )
    return ProfessionalVersionResponse.model_validate(result)


@router.get(
    "/{professional_id}/versions",
    response_model=PaginatedResponse[ProfessionalVersionListResponse],
    summary="List professional versions",
    description="List version history for a professional with pagination.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Professional not found",
        },
    },
)
async def list_professional_versions(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: ListProfessionalVersionsUC,
    pagination: PaginationParams = Depends(),
    filters: ProfessionalVersionFilter = Depends(
        filter_as_query(ProfessionalVersionFilter)
    ),
    sorting: ProfessionalVersionSorting = Depends(
        sorting_as_query(ProfessionalVersionSorting)
    ),
) -> PaginatedResponse[ProfessionalVersionListResponse]:
    """List version history for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        pagination=pagination,
        family_org_ids=ctx.family_org_ids,
        filters=filters,
        sorting=sorting,
    )

    return PaginatedResponse(
        items=[
            ProfessionalVersionListResponse(
                id=v.id,
                version_number=v.version_number,
                is_current=v.is_current,
                source_type=v.source_type,
                applied_at=v.applied_at,
                rejected_at=v.rejected_at,
                created_at=v.created_at,
                is_applied=v.is_applied,
                is_rejected=v.is_rejected,
                is_pending=v.is_pending,
                changes_count=len(v.diffs) if v.diffs else 0,
            )
            for v in result.items
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        has_next=result.has_next,
        has_previous=result.has_previous,
    )


@router.get(
    "/{professional_id}/versions/{version_id}",
    response_model=ProfessionalVersionDetailResponse,
    summary="Get professional version",
    description="Get a specific version with full details including diffs.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Version not found",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Version not found",
                            "value": {
                                "code": ProfessionalErrorCodes.VERSION_NOT_FOUND,
                                "message": "Versão do profissional não encontrada",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def get_professional_version(
    professional_id: UUID,
    version_id: UUID,
    ctx: OrganizationContext,
    use_case: GetProfessionalVersionUC,
) -> ProfessionalVersionDetailResponse:
    """Get a specific version with details."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        version_id=version_id,
        include_diffs=True,
    )
    return ProfessionalVersionDetailResponse.model_validate(result)


@router.post(
    "/{professional_id}/versions/{version_id}/apply",
    response_model=ProfessionalVersionResponse,
    summary="Apply a pending version",
    description=(
        "Apply a pending version to the professional. "
        "The version's snapshot data will be synced to the actual entities."
    ),
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Version not found",
            "content": {
                "application/json": {
                    "examples": {
                        "version_not_found": {
                            "summary": "Version not found",
                            "value": {
                                "code": ProfessionalErrorCodes.VERSION_NOT_FOUND,
                                "message": "Versão do profissional não encontrada",
                            },
                        },
                        "bank_not_found": {
                            "summary": "Bank not found",
                            "value": {
                                "code": ProfessionalErrorCodes.BANK_NOT_FOUND,
                                "message": "Banco não encontrado",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Version already applied or rejected",
            "content": {
                "application/json": {
                    "examples": {
                        "already_applied": {
                            "summary": "Version already applied",
                            "value": {
                                "code": ProfessionalErrorCodes.VERSION_ALREADY_APPLIED,
                                "message": "Esta versão já foi aplicada",
                            },
                        },
                        "already_rejected": {
                            "summary": "Version already rejected",
                            "value": {
                                "code": ProfessionalErrorCodes.VERSION_ALREADY_REJECTED,
                                "message": "Esta versão já foi rejeitada",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def apply_professional_version(
    professional_id: UUID,
    version_id: UUID,
    ctx: OrganizationContext,
    use_case: ApplyProfessionalVersionUC,
) -> ProfessionalVersionResponse:
    """Apply a pending version."""
    # We get the professional but the version is used
    await use_case.execute(
        organization_id=ctx.organization,
        version_id=version_id,
        applied_by=ctx.user,
        family_org_ids=ctx.family_org_ids,
    )

    # Get the updated version
    from src.modules.professionals.use_cases.professional_version import (
        GetProfessionalVersionUseCase,
    )

    # Re-fetch the version to return updated state
    get_use_case = GetProfessionalVersionUseCase(use_case.session)
    version = await get_use_case.execute(
        organization_id=ctx.organization,
        version_id=version_id,
    )
    return ProfessionalVersionResponse.model_validate(version)


@router.post(
    "/{professional_id}/versions/{version_id}/reject",
    response_model=ProfessionalVersionResponse,
    summary="Reject a pending version",
    description="Reject a pending version with a reason. Rejected versions cannot be applied.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Version not found",
        },
        409: {
            "model": ErrorResponse,
            "description": "Version already applied or rejected",
        },
    },
)
async def reject_professional_version(
    professional_id: UUID,
    version_id: UUID,
    data: ProfessionalVersionReject,
    ctx: OrganizationContext,
    use_case: RejectProfessionalVersionUC,
) -> ProfessionalVersionResponse:
    """Reject a pending version."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        version_id=version_id,
        data=data,
        rejected_by=ctx.user,
    )
    return ProfessionalVersionResponse.model_validate(result)
