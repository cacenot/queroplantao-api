"""Screening step routes."""

from uuid import UUID

from fastapi import APIRouter, status

from src.app.constants.error_codes import ScreeningErrorCodes
from src.app.dependencies import OrganizationContext
from src.modules.screening.domain.schemas import (
    # ClientValidationStepCompleteRequest,  # BROKEN - commented out
    ConversationStepCompleteRequest,
    DocumentReviewStepCompleteRequest,
    DocumentUploadStepCompleteRequest,
    ScreeningProcessStepResponse,
)
from src.modules.screening.domain.schemas.steps import (
    ConversationStepResponse,
    ProfessionalDataStepCompleteRequest,
    ProfessionalDataStepResponse,
)
from src.modules.screening.presentation.dependencies import (
    # CompleteClientValidationStepUC,  # BROKEN - commented out
    CompleteConversationStepUC,
    CompleteDocumentReviewStepUC,
    CompleteDocumentUploadStepUC,
    CompleteProfessionalDataStepUC,
    GoBackToStepUC,
    # SkipClientValidationUC,  # BROKEN - commented out
)
from src.shared.domain.schemas import ErrorResponse

router = APIRouter(tags=["Screening - Steps"])


# =============================================================================
# CONVERSATION STEP
# =============================================================================


@router.post(
    "/{screening_id}/steps/conversation/complete",
    response_model=ConversationStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalizar etapa de conversa",
    description="""
Finaliza a etapa de conversa inicial com o profissional.

**Outcomes:**
- `PROCEED`: Aprova a etapa e avança para PROFESSIONAL_DATA
- `REJECT`: Rejeita a etapa e encerra o processo de triagem

**Validações:**
- Processo deve existir e pertencer à organização
- Etapa de conversa deve existir para o processo
- Etapa deve estar em andamento (IN_PROGRESS)
- Usuário deve estar atribuído à etapa (se assigned_to estiver definido)
""",
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Não autorizado",
            "content": {
                "application/json": {
                    "examples": {
                        "not_assigned": {
                            "summary": "Etapa não atribuída ao usuário",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_NOT_ASSIGNED_TO_USER,
                                "message": "Esta etapa não está atribuída ao usuário atual",
                            },
                        },
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "process_not_found": {
                            "summary": "Processo não encontrado",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
                                "message": "Processo de triagem não encontrado",
                            },
                        },
                        "step_not_found": {
                            "summary": "Etapa não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_NOT_FOUND,
                                "message": "Etapa de triagem não encontrada",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Validação falhou",
            "content": {
                "application/json": {
                    "examples": {
                        "already_completed": {
                            "summary": "Etapa já concluída",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_ALREADY_COMPLETED,
                                "message": "Esta etapa já foi concluída",
                            },
                        },
                        "not_in_progress": {
                            "summary": "Etapa não está em andamento",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_NOT_IN_PROGRESS,
                                "message": "Esta etapa não está em andamento",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def complete_conversation_step(
    screening_id: UUID,
    data: ConversationStepCompleteRequest,
    ctx: OrganizationContext,
    use_case: CompleteConversationStepUC,
) -> ConversationStepResponse:
    """Complete the conversation step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        data=data,
        completed_by=ctx.user,
    )


# =============================================================================
# PROFESSIONAL DATA STEP
# =============================================================================


@router.post(
    "/{screening_id}/steps/professional-data/complete",
    response_model=ProfessionalDataStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalizar etapa de dados do profissional",
    description="""
Finaliza a etapa de coleta de dados do profissional.

Esta etapa valida que os dados do profissional estão completos.
O frontend exibe os dados do profissional para o usuário revisar.
O usuário pode criar/editar o profissional usando os endpoints /composite
antes de completar esta etapa.

**Validações:**
- Processo deve existir e pertencer à organização
- Etapa de dados do profissional deve existir para o processo
- Etapa deve estar em andamento (IN_PROGRESS)
- Usuário deve estar atribuído à etapa (se assigned_to estiver definido)
- Profissional deve estar vinculado ao processo (organization_professional_id)
- Profissional deve ter pelo menos uma qualificação
- Se expected_professional_type estiver definido, deve corresponder
- Se expected_specialty_id estiver definido, profissional deve ter essa especialidade
""",
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Não autorizado",
            "content": {
                "application/json": {
                    "examples": {
                        "not_assigned": {
                            "summary": "Etapa não atribuída ao usuário",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_NOT_ASSIGNED_TO_USER,
                                "message": "Esta etapa não está atribuída ao usuário atual",
                            },
                        },
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "process_not_found": {
                            "summary": "Processo não encontrado",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
                                "message": "Processo de triagem não encontrado",
                            },
                        },
                        "step_not_found": {
                            "summary": "Etapa não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_NOT_FOUND,
                                "message": "Etapa de triagem não encontrada",
                            },
                        },
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Validação falhou",
            "content": {
                "application/json": {
                    "examples": {
                        "already_completed": {
                            "summary": "Etapa já concluída",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_ALREADY_COMPLETED,
                                "message": "Esta etapa já foi concluída",
                            },
                        },
                        "not_in_progress": {
                            "summary": "Etapa não está em andamento",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_NOT_IN_PROGRESS,
                                "message": "Esta etapa não está em andamento",
                            },
                        },
                        "professional_not_linked": {
                            "summary": "Profissional não vinculado",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROFESSIONAL_NOT_LINKED,
                                "message": "Nenhum profissional vinculado ao processo de triagem",
                            },
                        },
                        "no_qualification": {
                            "summary": "Sem qualificação",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROFESSIONAL_NO_QUALIFICATION,
                                "message": "O profissional não possui qualificação cadastrada",
                            },
                        },
                        "type_mismatch": {
                            "summary": "Tipo não corresponde",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_PROFESSIONAL_TYPE_MISMATCH,
                                "message": "Tipo de profissional não corresponde ao esperado",
                            },
                        },
                        "specialty_mismatch": {
                            "summary": "Especialidade não encontrada",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_SPECIALTY_MISMATCH,
                                "message": "O profissional não possui a especialidade requerida",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def complete_professional_data_step(
    screening_id: UUID,
    data: ProfessionalDataStepCompleteRequest,
    ctx: OrganizationContext,
    use_case: CompleteProfessionalDataStepUC,
) -> ProfessionalDataStepResponse:
    """Complete the professional data step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        data=data,
        completed_by=ctx.user,
    )


# =============================================================================
# DOCUMENT UPLOAD STEP
# =============================================================================


@router.post(
    "/{screening_id}/steps/{step_id}/document-upload/complete",
    response_model=ScreeningProcessStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalizar etapa de upload de documentos",
    description="Finaliza a etapa de upload de documentos.",
    responses={
        404: {"model": ErrorResponse, "description": "Não encontrado"},
        422: {
            "model": ErrorResponse,
            "description": "Validação falhou",
            "content": {
                "application/json": {
                    "examples": {
                        "no_documents": {
                            "summary": "Nenhum documento enviado",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_DOCUMENTS_NOT_UPLOADED,
                                "message": "Nenhum documento foi enviado nesta etapa",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def complete_document_upload_step(
    screening_id: UUID,
    step_id: UUID,
    data: DocumentUploadStepCompleteRequest,
    ctx: OrganizationContext,
    use_case: CompleteDocumentUploadStepUC,
) -> ScreeningProcessStepResponse:
    """Complete the document upload step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        step_id=step_id,
        data=data,
        completed_by=ctx.user,
    )


# =============================================================================
# DOCUMENT REVIEW STEP
# =============================================================================


@router.post(
    "/{screening_id}/steps/{step_id}/document-review/complete",
    response_model=ScreeningProcessStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalizar etapa de revisão de documentos",
    description="Finaliza a etapa de revisão de documentos. Todos os documentos devem estar aprovados ou rejeitados.",
    responses={
        404: {"model": ErrorResponse, "description": "Não encontrado"},
        422: {
            "model": ErrorResponse,
            "description": "Validação falhou",
            "content": {
                "application/json": {
                    "examples": {
                        "pending_review": {
                            "summary": "Documentos pendentes de revisão",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_DOCUMENTS_NOT_REVIEWED,
                                "message": "Há documentos pendentes de revisão",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def complete_document_review_step(
    screening_id: UUID,
    step_id: UUID,
    data: DocumentReviewStepCompleteRequest,
    ctx: OrganizationContext,
    use_case: CompleteDocumentReviewStepUC,
) -> ScreeningProcessStepResponse:
    """Complete the document review step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        step_id=step_id,
        data=data,
        completed_by=ctx.user,
    )


# =============================================================================
# CLIENT VALIDATION STEP - REMOVED (broken due to refactoring)
# =============================================================================
# The following endpoints have been removed because the underlying use cases
# are broken and need reimplementation:
# - POST /{screening_id}/steps/{step_id}/client-validation/complete
# - POST /{screening_id}/client-validation/skip
#
# See the use case files for details on what needs to be reimplemented:
# - src/modules/screening/use_cases/screening_step/client_validation_step_complete_use_case.py
# - src/modules/screening/use_cases/screening_validation/screening_client_validation_use_case.py
# =============================================================================


# =============================================================================
# GO BACK (New use case)
# =============================================================================


@router.post(
    "/{screening_id}/steps/{step_id}/go-back",
    response_model=ScreeningProcessStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Voltar para etapa anterior",
    description="Volta para uma etapa anterior, resetando as posteriores.",
    responses={
        404: {"model": ErrorResponse, "description": "Não encontrado"},
        422: {
            "model": ErrorResponse,
            "description": "Não é possível voltar",
            "content": {
                "application/json": {
                    "examples": {
                        "cannot_go_back": {
                            "summary": "Não pode voltar para esta etapa",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_CANNOT_GO_BACK,
                                "message": "Não é possível voltar para esta etapa",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def go_back_to_step(
    screening_id: UUID,
    step_id: UUID,
    ctx: OrganizationContext,
    use_case: GoBackToStepUC,
) -> ScreeningProcessStepResponse:
    """Go back to a previous step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        family_org_ids=ctx.family_org_ids,
        screening_id=screening_id,
        target_step_id=step_id,
        requested_by=ctx.user,
    )
