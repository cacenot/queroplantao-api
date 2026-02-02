"""Screening document routes.

Handles document configuration, upload, and review within a screening workflow.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile, status

from src.app.constants.error_codes import ProfessionalErrorCodes, ScreeningErrorCodes
from src.app.dependencies import OrganizationContext
from src.shared.domain.schemas import ErrorResponse
from src.modules.screening.domain.schemas.screening_document import (
    ScreeningDocumentResponse,
)
from src.modules.screening.domain.schemas.steps import (
    ConfigureDocumentsRequest,
    DocumentUploadStepResponse,
    ReviewDocumentRequest,
)
from src.modules.screening.presentation.dependencies.screening_document import (
    ConfigureDocumentsUC,
    ReviewDocumentUC,
    UploadDocumentUC,
)
from src.modules.screening.presentation.dependencies import ReuseDocumentUC

router = APIRouter(tags=["Screening - Documents"])


# =============================================================================
# DOCUMENT UPLOAD STEP ENDPOINTS
# =============================================================================


@router.post(
    "/{screening_id}/steps/document-upload/configure",
    response_model=DocumentUploadStepResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configurar documentos",
    description=(
        "Configura a lista de documentos necessários para a triagem. "
        "Transiciona o step de PENDING para IN_PROGRESS."
    ),
)
async def configure_documents(
    screening_id: UUID,
    data: ConfigureDocumentsRequest,
    ctx: OrganizationContext,
    use_case: ConfigureDocumentsUC,
) -> DocumentUploadStepResponse:
    """Configure required documents for the screening."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        data=data,
        configured_by=ctx.user,
    )


@router.post(
    "/{screening_id}/documents/{document_id}/upload",
    response_model=ScreeningDocumentResponse,
    summary="Upload de documento",
    description=(
        "Faz upload de um documento para a triagem. "
        "O arquivo é enviado via multipart/form-data e o backend faz upload "
        "para o Firebase Storage, cria o ProfessionalDocument (is_pending=True) "
        "e o vincula ao ScreeningDocument, inferindo qualification_id e specialty_id "
        "com base na categoria do documento."
    ),
)
async def upload_document(
    screening_id: UUID,
    document_id: UUID,
    ctx: OrganizationContext,
    use_case: UploadDocumentUC,
    file: Annotated[
        UploadFile, File(description="Arquivo do documento (PDF, JPEG, PNG, WebP)")
    ],
    expires_at: Annotated[
        datetime | None, Form(description="Data de validade do documento (UTC)")
    ] = None,
    notes: Annotated[
        str | None, Form(description="Observações sobre o documento")
    ] = None,
) -> ScreeningDocumentResponse:
    """Upload a document to the screening workflow."""
    # Note: screening_id is used for authorization check in the future
    _ = screening_id
    return await use_case.execute(
        screening_document_id=document_id,
        file=file,
        uploaded_by=ctx.user,
        expires_at=expires_at,
        notes=notes,
    )


@router.post(
    "/{screening_id}/documents/{document_id}/reuse",
    response_model=ScreeningDocumentResponse,
    summary="Reutilizar documento existente",
    description=(
        "Reutiliza um documento já aprovado de triagens anteriores. "
        "Apenas documentos que não estão pendentes (is_pending=False) podem ser reutilizados. "
        "O documento reutilizado recebe status PENDING_REVIEW e segue para revisão."
    ),
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "screening_document_not_found": {
                            "summary": "Documento de triagem não encontrado",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_DOCUMENT_NOT_FOUND,
                                "message": "Documento de triagem não encontrado",
                            },
                        },
                        "professional_document_not_found": {
                            "summary": "Documento do profissional não encontrado",
                            "value": {
                                "code": ProfessionalErrorCodes.DOCUMENT_NOT_FOUND,
                                "message": "Documento do profissional não encontrado",
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
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "examples": {
                        "step_not_in_progress": {
                            "summary": "Etapa não está em andamento",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_STEP_NOT_IN_PROGRESS,
                                "message": "Esta etapa não está em andamento",
                            },
                        },
                        "invalid_status": {
                            "summary": "Status inválido para reutilização",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_DOCUMENT_INVALID_STATUS,
                                "message": "Documento não pode ser reutilizado no status APPROVED",
                            },
                        },
                        "reuse_pending": {
                            "summary": "Documento pendente",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_DOCUMENT_REUSE_PENDING,
                                "message": "Documento pendente não pode ser reutilizado. Apenas documentos aprovados podem ser reutilizados.",
                            },
                        },
                        "type_mismatch": {
                            "summary": "Tipo de documento não corresponde",
                            "value": {
                                "code": ScreeningErrorCodes.SCREENING_DOCUMENT_TYPE_MISMATCH,
                                "message": "Tipo de documento não corresponde ao requisitado. Esperado: 00000000-0000-0000-0000-000000000000, encontrado: 11111111-1111-1111-1111-111111111111",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def reuse_document(
    screening_id: UUID,
    document_id: UUID,
    professional_document_id: UUID,
    ctx: OrganizationContext,
    use_case: ReuseDocumentUC,
) -> ScreeningDocumentResponse:
    """Reuse an existing approved document."""
    # Note: screening_id is used for authorization check in the future
    _ = screening_id
    return await use_case.execute(
        screening_document_id=document_id,
        professional_document_id=professional_document_id,
        reused_by=ctx.user,
    )


# =============================================================================
# DOCUMENT REVIEW STEP ENDPOINTS
# =============================================================================


@router.post(
    "/{screening_id}/documents/{document_id}/review",
    response_model=ScreeningDocumentResponse,
    summary="Revisar documento",
    description=(
        "Revisa um documento individual. "
        "Define como APPROVED ou CORRECTION_NEEDED (com motivo)."
    ),
)
async def review_document(
    screening_id: UUID,
    document_id: UUID,
    data: ReviewDocumentRequest,
    ctx: OrganizationContext,
    use_case: ReviewDocumentUC,
) -> ScreeningDocumentResponse:
    """Review a screening document."""
    # Note: screening_id is used for authorization check in the future
    _ = screening_id
    return await use_case.execute(
        screening_document_id=document_id,
        data=data,
        reviewed_by=ctx.user,
    )
