"""Screening alert routes."""

from uuid import UUID

from fastapi import APIRouter, status

from src.app.constants.error_codes import ScreeningErrorCodes
from src.app.dependencies import OrganizationContext
from src.modules.screening.domain.schemas import (
    ScreeningAlertCreate,
    ScreeningAlertListResponse,
    ScreeningAlertReject,
    ScreeningAlertResolve,
    ScreeningAlertResponse,
)
from src.modules.screening.presentation.dependencies import (
    CreateScreeningAlertUC,
    ListScreeningAlertsUC,
    RejectScreeningAlertUC,
    ResolveScreeningAlertUC,
)
from src.shared.domain.schemas import ErrorResponse

router = APIRouter()


@router.post(
    "/{screening_id}/alerts",
    response_model=ScreeningAlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar alerta",
    description="""
Cria um alerta para um processo de triagem.

**Comportamento:**
- Qualquer usuário autorizado pode criar um alerta
- Apenas um alerta pendente por vez
- O alerta bloqueia o andamento da triagem
- O status da triagem muda para PENDING_SUPERVISOR

**Categorias disponíveis:**
- DOCUMENT: Problema com documentos
- DATA: Dados inconsistentes
- BEHAVIOR: Comportamento inadequado
- COMPLIANCE: Problemas de conformidade
- QUALIFICATION: Qualificação insuficiente
- OTHER: Outros
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
                                "message": "Triagem não encontrada",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflito",
            "content": {
                "application/json": {
                    "examples": {
                        "alert_exists": {
                            "summary": "Alerta pendente já existe",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_ALERT_ALREADY_EXISTS,
                                "message": "Já existe um alerta pendente para esta triagem",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_status": {
                            "summary": "Status inválido",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_INVALID_STATUS_TRANSITION,
                                "message": "Não é possível criar alerta para triagem com status atual",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def create_alert(
    screening_id: UUID,
    data: ScreeningAlertCreate,
    ctx: OrganizationContext,
    use_case: CreateScreeningAlertUC,
) -> ScreeningAlertResponse:
    """Create a new alert for a screening process."""
    return await use_case.execute(
        organization_id=ctx.organization,
        process_id=screening_id,
        data=data,
        triggered_by=ctx.user,
        triggered_by_name=ctx.context.full_name,
        triggered_by_role_name=ctx.context.organization_role_name or "Usuário",
    )


@router.get(
    "/{screening_id}/alerts",
    response_model=ScreeningAlertListResponse,
    summary="Listar alertas",
    description="""
Lista todos os alertas de um processo de triagem.

**Retorna:**
- Lista de alertas (resolvidos e pendentes)
- Contagem total
- Contagem de alertas pendentes
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
                                "message": "Triagem não encontrada",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def list_alerts(
    screening_id: UUID,
    ctx: OrganizationContext,
    use_case: ListScreeningAlertsUC,
) -> ScreeningAlertListResponse:
    """List all alerts for a screening process."""
    return await use_case.execute(
        organization_id=ctx.organization,
        process_id=screening_id,
    )


@router.post(
    "/{screening_id}/alerts/{alert_id}/resolve",
    response_model=ScreeningAlertResponse,
    summary="Resolver alerta",
    description="""
Resolve um alerta, permitindo que a triagem continue.

**Comportamento:**
- Apenas supervisores podem resolver alertas
- O alerta é marcado como resolvido
- O status da triagem volta para IN_PROGRESS
- Uma nota é adicionada com a resolução
""",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "process_not_found": {
                            "summary": "Triagem não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
                                "message": "Triagem não encontrada",
                            },
                        },
                        "alert_not_found": {
                            "summary": "Alerta não encontrado",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_ALERT_NOT_FOUND,
                                "message": "Alerta não encontrado",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflito",
            "content": {
                "application/json": {
                    "examples": {
                        "already_resolved": {
                            "summary": "Alerta já resolvido",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_ALERT_ALREADY_RESOLVED,
                                "message": "Este alerta já foi resolvido",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def resolve_alert(
    screening_id: UUID,
    alert_id: UUID,
    data: ScreeningAlertResolve,
    ctx: OrganizationContext,
    use_case: ResolveScreeningAlertUC,
) -> ScreeningAlertResponse:
    """Resolve an alert, allowing the screening to continue."""
    return await use_case.execute(
        organization_id=ctx.organization,
        process_id=screening_id,
        alert_id=alert_id,
        data=data,
        resolved_by=ctx.user,
        resolved_by_name=ctx.context.full_name,
        resolved_by_role_name=ctx.context.organization_role_name or "Supervisor",
    )


@router.post(
    "/{screening_id}/alerts/{alert_id}/reject",
    response_model=ScreeningAlertResponse,
    summary="Rejeitar triagem via alerta",
    description="""
Rejeita a triagem através do alerta.

**Comportamento:**
- Apenas supervisores podem rejeitar
- O alerta é marcado como resolvido
- O status da triagem muda para REJECTED
- O motivo de rejeição é registrado na triagem
""",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "process_not_found": {
                            "summary": "Triagem não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
                                "message": "Triagem não encontrada",
                            },
                        },
                        "alert_not_found": {
                            "summary": "Alerta não encontrado",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_ALERT_NOT_FOUND,
                                "message": "Alerta não encontrado",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflito",
            "content": {
                "application/json": {
                    "examples": {
                        "already_resolved": {
                            "summary": "Alerta já resolvido",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_ALERT_ALREADY_RESOLVED,
                                "message": "Este alerta já foi resolvido",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def reject_via_alert(
    screening_id: UUID,
    alert_id: UUID,
    data: ScreeningAlertReject,
    ctx: OrganizationContext,
    use_case: RejectScreeningAlertUC,
) -> ScreeningAlertResponse:
    """Reject the screening through an alert."""
    return await use_case.execute(
        organization_id=ctx.organization,
        process_id=screening_id,
        alert_id=alert_id,
        data=data,
        rejected_by=ctx.user,
        rejected_by_name=ctx.context.full_name,
        rejected_by_role_name=ctx.context.organization_role_name or "Supervisor",
    )
