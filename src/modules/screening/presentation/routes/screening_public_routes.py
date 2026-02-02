"""Public screening routes (token-based access)."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile

from src.modules.screening.domain.schemas import (
    ScreeningDocumentResponse,
    ScreeningProcessDetailResponse,
)
from src.modules.screening.presentation.dependencies import (
    GetScreeningProcessByTokenUC,
    UploadDocumentUC,
)

router = APIRouter(tags=["Screening - Public"])


@router.get(
    "/{token}",
    response_model=ScreeningProcessDetailResponse,
    summary="Acessar triagem por token",
    description="Acessa o processo de triagem usando o token público (para profissionais)",
)
async def get_screening_by_token(
    token: str,
    use_case: GetScreeningProcessByTokenUC,
) -> ScreeningProcessDetailResponse:
    """Get screening process by public access token with all details."""
    return await use_case.execute(token=token)


@router.post(
    "/{token}/documents/{document_id}/upload",
    response_model=ScreeningDocumentResponse,
    summary="Upload de documento (público)",
    description=(
        "Faz upload de um documento usando o token público. "
        "O arquivo é enviado via multipart/form-data e o backend faz upload "
        "para o Firebase Storage, cria o ProfessionalDocument e o vincula ao ScreeningDocument."
    ),
)
async def upload_document_by_token(
    token: str,
    document_id: UUID,
    get_screening_use_case: GetScreeningProcessByTokenUC,
    upload_use_case: UploadDocumentUC,
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
    """Upload a document using public token."""
    # Validate the token and get screening (ensures token is valid)
    await get_screening_use_case.execute(token=token)

    # Upload the document (without user context)
    return await upload_use_case.execute(
        screening_document_id=document_id,
        file=file,
        uploaded_by=None,  # No authenticated user
        expires_at=expires_at,
        notes=notes,
    )
