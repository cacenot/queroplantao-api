"""Screening process routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.app.dependencies import OrganizationContext
from src.modules.screening.domain.schemas import (
    ScreeningProcessApprove,
    ScreeningProcessCreate,
    ScreeningProcessDetailResponse,
    ScreeningProcessReject,
    ScreeningProcessResponse,
)
from src.modules.screening.infrastructure.filters import (
    ScreeningProcessFilter,
    ScreeningProcessSorting,
)
from src.modules.screening.presentation.dependencies import (
    ApproveScreeningProcessUC,
    CancelScreeningProcessUC,
    CreateScreeningProcessUC,
    GetScreeningProcessUC,
    ListMyScreeningProcessesUC,
    ListScreeningProcessesUC,
    RejectScreeningProcessUC,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ScreeningProcessDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar triagem",
    description="Cria um novo processo de triagem para um profissional (Etapa 1 - Conversa/Criação)",
)
async def create_screening_process(
    data: ScreeningProcessCreate,
    ctx: OrganizationContext,
    use_case: CreateScreeningProcessUC,
) -> ScreeningProcessDetailResponse:
    """Create a new screening process."""
    return await use_case.execute(
        organization_id=ctx.organization,
        data=data,
        created_by=ctx.user,
        family_org_ids=ctx.family_org_ids,
    )


@router.get(
    "/",
    response_model=PaginatedResponse[ScreeningProcessResponse],
    summary="Listar triagens",
    description="Lista todos os processos de triagem da organização",
)
async def list_screening_processes(
    ctx: OrganizationContext,
    use_case: ListScreeningProcessesUC,
    pagination: PaginationParams = Depends(),
    filters: ScreeningProcessFilter = Depends(filter_as_query(ScreeningProcessFilter)),
    sorting: ScreeningProcessSorting = Depends(
        sorting_as_query(ScreeningProcessSorting)
    ),
) -> PaginatedResponse[ScreeningProcessResponse]:
    """List all screening processes for the organization."""
    return await use_case.execute(
        organization_id=ctx.organization,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )


@router.get(
    "/me",
    response_model=PaginatedResponse[ScreeningProcessResponse],
    summary="Minhas triagens",
    description="Lista as triagens atribuídas ao usuário atual",
)
async def list_my_screening_processes(
    ctx: OrganizationContext,
    use_case: ListMyScreeningProcessesUC,
    pagination: PaginationParams = Depends(),
    filters: ScreeningProcessFilter = Depends(filter_as_query(ScreeningProcessFilter)),
    sorting: ScreeningProcessSorting = Depends(
        sorting_as_query(ScreeningProcessSorting)
    ),
) -> PaginatedResponse[ScreeningProcessResponse]:
    """List screening processes assigned to the current user."""
    return await use_case.execute(
        organization_id=ctx.organization,
        actor_id=ctx.user,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )


@router.get(
    "/{screening_id}",
    response_model=ScreeningProcessDetailResponse,
    summary="Obter triagem",
    description="Obtém detalhes de um processo de triagem específico com etapas e documentos",
)
async def get_screening_process(
    screening_id: UUID,
    ctx: OrganizationContext,
    use_case: GetScreeningProcessUC,
) -> ScreeningProcessDetailResponse:
    """Get a specific screening process with all details."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
    )


@router.post(
    "/{screening_id}/approve",
    response_model=ScreeningProcessResponse,
    summary="Aprovar triagem",
    description="Aprova o processo de triagem (após todas as etapas concluídas)",
)
async def approve_screening_process(
    screening_id: UUID,
    data: ScreeningProcessApprove,
    ctx: OrganizationContext,
    use_case: ApproveScreeningProcessUC,
) -> ScreeningProcessResponse:
    """Approve a screening process."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        approved_by=ctx.user,
        notes=data.notes,
    )


@router.post(
    "/{screening_id}/reject",
    response_model=ScreeningProcessResponse,
    summary="Rejeitar triagem",
    description="Rejeita o processo de triagem com motivo",
)
async def reject_screening_process(
    screening_id: UUID,
    data: ScreeningProcessReject,
    ctx: OrganizationContext,
    use_case: RejectScreeningProcessUC,
) -> ScreeningProcessResponse:
    """Reject a screening process."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        rejected_by=ctx.user,
        reason=data.reason,
    )


@router.post(
    "/{screening_id}/cancel",
    response_model=ScreeningProcessResponse,
    summary="Cancelar triagem",
    description="Cancela o processo de triagem",
)
async def cancel_screening_process(
    screening_id: UUID,
    ctx: OrganizationContext,
    use_case: CancelScreeningProcessUC,
    reason: str | None = None,
) -> ScreeningProcessResponse:
    """Cancel a screening process."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        cancelled_by=ctx.user,
        reason=reason,
    )
