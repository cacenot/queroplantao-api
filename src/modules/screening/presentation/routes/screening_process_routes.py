"""Screening process routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.app.constants.error_codes import ScreeningErrorCodes
from src.app.dependencies import OrganizationContext
from src.modules.screening.domain.schemas import (
    ScreeningProcessCancel,
    ScreeningProcessCreate,
    ScreeningProcessDetailResponse,
    ScreeningProcessListResponse,
    ScreeningProcessResponse,
)
from src.modules.screening.infrastructure.filters import (
    ScreeningProcessFilter,
    ScreeningProcessSorting,
)
from src.modules.screening.presentation.dependencies import (
    CancelScreeningProcessUC,
    CreateScreeningProcessUC,
    FinalizeScreeningProcessUC,
    GetScreeningProcessUC,
    ListScreeningProcessesUC,
)
from src.shared.domain.schemas import ErrorResponse

router = APIRouter()


@router.post(
    "/",
    response_model=ScreeningProcessDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar triagem",
    description="""
Cria um novo processo de triagem para um profissional (Etapa 1 - Conversa/Criação).

**Steps obrigatórios (sempre criados):**
- CONVERSATION: Conversa inicial por telefone
- PROFESSIONAL_DATA: Dados pessoais, qualificações e especialidades
- DOCUMENT_UPLOAD: Upload de documentos
- DOCUMENT_REVIEW: Revisão dos documentos

**Steps opcionais (configuráveis):**
- PAYMENT_INFO: Dados bancários e de empresa (default: habilitado)
- SUPERVISOR_REVIEW: Revisão por supervisor (default: desabilitado)
- CLIENT_VALIDATION: Validação pelo cliente (default: desabilitado, auto-habilitado se client_company_id fornecido)
""",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Conflito",
            "content": {
                "application/json": {
                    "examples": {
                        "active_exists": {
                            "summary": "Triagem ativa já existe",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_ACTIVE_EXISTS,
                                "message": "Já existe uma triagem ativa para este CPF",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação",
        },
    },
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
    response_model=PaginatedResponse[ScreeningProcessListResponse],
    summary="Listar triagens",
    description="""
Lista todos os processos de triagem da organização.

**Filtros disponíveis:**
- `status`: Filtra por status (IN_PROGRESS, APPROVED, REJECTED, CANCELLED)
- `search`: Busca por nome ou CPF do profissional
- `owner_id`: Filtra por responsável
- `actor_id`: Filtra por usuário responsável atual (current_actor_id)
- `created_after`: Filtra por data de criação

**Ordenação:**
- `id`: Ordena por ID (UUID v7 = ordem temporal)
- `created_at`: Ordena por data de criação
- `status`: Ordena por status
""",
)
async def list_screening_processes(
    ctx: OrganizationContext,
    use_case: ListScreeningProcessesUC,
    pagination: PaginationParams = Depends(),
    filters: ScreeningProcessFilter = Depends(filter_as_query(ScreeningProcessFilter)),
    sorting: ScreeningProcessSorting = Depends(
        sorting_as_query(ScreeningProcessSorting)
    ),
) -> PaginatedResponse[ScreeningProcessListResponse]:
    """List all screening processes for the organization."""
    return await use_case.execute(
        organization_id=ctx.organization,
        pagination=pagination,
        family_org_ids=ctx.family_org_ids,
        filters=filters,
        sorting=sorting,
    )


@router.get(
    "/{screening_id}",
    response_model=ScreeningProcessDetailResponse,
    summary="Obter triagem",
    description="""
Obtém detalhes completos de um processo de triagem específico.

**Inclui:**
- Dados do profissional
- Lista de steps com status e ordem
- Documentos associados
- Histórico de atribuições
""",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Triagem não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
                                "message": "Processo de triagem não encontrado",
                            },
                        },
                    }
                }
            },
        },
    },
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
        family_org_ids=ctx.family_org_ids,
    )


@router.post(
    "/{screening_id}/cancel",
    response_model=ScreeningProcessResponse,
    summary="Cancelar triagem",
    description="""
Cancela o processo de triagem com motivo obrigatório.

**Regras:**
- Não é possível cancelar triagens já finalizadas (APPROVED, REJECTED, CANCELLED)
- Todos os steps ativos (PENDING ou IN_PROGRESS) serão marcados como CANCELLED
- O motivo deve ter no mínimo 10 caracteres
""",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Triagem não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
                                "message": "Processo de triagem não encontrado",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflito - Não é possível cancelar",
            "content": {
                "application/json": {
                    "examples": {
                        "cannot_cancel": {
                            "summary": "Não é possível cancelar",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_CANNOT_CANCEL,
                                "message": "Não é possível cancelar um processo com status APPROVED",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação (motivo muito curto)",
        },
    },
)
async def cancel_screening_process(
    screening_id: UUID,
    data: ScreeningProcessCancel,
    ctx: OrganizationContext,
    use_case: CancelScreeningProcessUC,
) -> ScreeningProcessResponse:
    """Cancel a screening process."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        cancelled_by=ctx.user,
        reason=data.reason,
        family_org_ids=ctx.family_org_ids,
    )


@router.post(
    "/{screening_id}/finalize",
    response_model=ScreeningProcessResponse,
    summary="Finalizar triagem",
    description="""
Finaliza o processo de triagem e aprova o profissional.

**Ações realizadas:**
- Valida que todas as etapas obrigatórias foram concluídas
- Promove todos os documentos pendentes (is_pending=False)
- Atualiza o status da triagem para APPROVED

**Documentos pendentes:**
Documentos criados durante a triagem (source_type=SCREENING) ficam com is_pending=True
até a triagem ser finalizada. Isso permite que:
- O profissional visualize os documentos que está enviando
- O sistema mantenha histórico de versões
- Documentos de triagens canceladas/rejeitadas sejam automaticamente excluídos

**Regras:**
- Só é possível finalizar triagens com status IN_PROGRESS
- Todas as etapas obrigatórias devem estar COMPLETED ou APPROVED
""",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Triagem não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
                                "message": "Processo de triagem não encontrado",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação - Etapas pendentes",
            "content": {
                "application/json": {
                    "examples": {
                        "incomplete_steps": {
                            "summary": "Etapas incompletas",
                            "value": {
                                "code": "VALIDATION_ERROR",
                                "message": "Não é possível finalizar a triagem. Etapas pendentes: Revisão de Documentos, Dados de Pagamento",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def finalize_screening_process(
    screening_id: UUID,
    ctx: OrganizationContext,
    use_case: FinalizeScreeningProcessUC,
) -> ScreeningProcessResponse:
    """Finalize a screening process and promote pending documents."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        finalized_by=ctx.user,
        family_org_ids=ctx.family_org_ids,
    )
