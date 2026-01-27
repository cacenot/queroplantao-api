"""Screening step routes."""

from uuid import UUID

from fastapi import APIRouter, status

from src.app.constants.error_codes import ScreeningErrorCodes
from src.app.dependencies import OrganizationContext
from src.modules.screening.domain.schemas import (
    ClientValidationStepCompleteRequest,
    ConversationStepCompleteRequest,
    DocumentReviewStepCompleteRequest,
    DocumentUploadStepCompleteRequest,
    ScreeningProcessStepResponse,
    SimpleStepCompleteRequest,
)
from src.modules.screening.presentation.dependencies import (
    CompleteClientValidationStepUC,
    CompleteConversationStepUC,
    CompleteDocumentReviewStepUC,
    CompleteDocumentUploadStepUC,
    CompleteSimpleStepUC,
    GoBackToStepUC,
    SkipClientValidationUC,
)
from src.shared.domain.schemas import ErrorResponse

router = APIRouter()


# =============================================================================
# CONVERSATION STEP
# =============================================================================


@router.post(
    "/{screening_id}/steps/{step_id}/conversation/complete",
    response_model=ScreeningProcessStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalizar etapa de conversa",
    description="Finaliza a etapa de conversa inicial com o profissional.",
    responses={
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
                        "invalid_type": {
                            "summary": "Tipo de etapa inválido",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_INVALID_TYPE,
                                "message": "Tipo de etapa inválido para esta operação",
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
    step_id: UUID,
    data: ConversationStepCompleteRequest,
    ctx: OrganizationContext,
    use_case: CompleteConversationStepUC,
) -> ScreeningProcessStepResponse:
    """Complete the conversation step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        step_id=step_id,
        data=data,
        completed_by=ctx.user,
    )


# =============================================================================
# SIMPLE STEPS (Data collection)
# =============================================================================


@router.post(
    "/{screening_id}/steps/{step_id}/simple/complete",
    response_model=ScreeningProcessStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalizar etapa simples",
    description="Finaliza uma etapa simples de coleta de dados (PROFESSIONAL_DATA, QUALIFICATION, SPECIALTY, EDUCATION, COMPANY, BANK_ACCOUNT).",
    responses={
        404: {"model": ErrorResponse, "description": "Não encontrado"},
        422: {"model": ErrorResponse, "description": "Validação falhou"},
    },
)
async def complete_simple_step(
    screening_id: UUID,
    step_id: UUID,
    data: SimpleStepCompleteRequest,
    ctx: OrganizationContext,
    use_case: CompleteSimpleStepUC,
) -> ScreeningProcessStepResponse:
    """Complete a simple step (PROFESSIONAL_DATA, QUALIFICATION, etc.)."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        step_id=step_id,
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
# CLIENT VALIDATION STEP (New endpoint)
# =============================================================================


@router.post(
    "/{screening_id}/steps/{step_id}/client-validation/complete",
    response_model=ScreeningProcessStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalizar validação do cliente (via step)",
    description="Finaliza a etapa de validação pelo cliente com step_id específico.",
    responses={
        404: {"model": ErrorResponse, "description": "Não encontrado"},
        422: {
            "model": ErrorResponse,
            "description": "Validação falhou",
            "content": {
                "application/json": {
                    "examples": {
                        "not_required": {
                            "summary": "Validação não necessária",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_CLIENT_VALIDATION_NOT_REQUIRED,
                                "message": "Validação do cliente não é necessária",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def complete_client_validation_step(
    screening_id: UUID,
    step_id: UUID,
    data: ClientValidationStepCompleteRequest,
    ctx: OrganizationContext,
    use_case: CompleteClientValidationStepUC,
) -> ScreeningProcessStepResponse:
    """Complete the client validation step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        step_id=step_id,
        data=data,
        completed_by=ctx.user,
    )


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
        screening_id=screening_id,
        target_step_id=step_id,
        requested_by=ctx.user,
    )


# =============================================================================
# CLIENT VALIDATION SKIP
# =============================================================================


@router.post(
    "/{screening_id}/client-validation/skip",
    response_model=ScreeningProcessStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Pular validação do cliente",
    description="Pula a etapa de validação do cliente (quando não é obrigatória)",
)
async def skip_client_validation(
    screening_id: UUID,
    ctx: OrganizationContext,
    use_case: SkipClientValidationUC,
    reason: str | None = None,
) -> ScreeningProcessStepResponse:
    """Skip the client validation step."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        skipped_by=ctx.user,
        reason=reason,
    )
