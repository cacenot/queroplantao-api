"""Public screening routes (token-based access)."""

from uuid import UUID

from fastapi import APIRouter

from src.modules.screening.domain.schemas import (
    ScreeningDocumentResponse,
    ScreeningProcessDetailResponse,
    UploadDocumentRequest,
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
    description="Faz upload de um documento usando o token público",
)
async def upload_document_by_token(
    token: str,
    document_id: UUID,
    data: UploadDocumentRequest,
    get_screening_use_case: GetScreeningProcessByTokenUC,
    upload_use_case: UploadDocumentUC,
) -> ScreeningDocumentResponse:
    """Upload a document using public token."""
    # First validate the token and get screening
    screening = await get_screening_use_case.execute(token=token)

    # Then upload the document (without user context)
    return await upload_use_case.execute(
        screening_id=screening.id,
        required_document_id=document_id,
        data=data,
        uploaded_by=None,  # No authenticated user
    )
