"""Screening document routes."""

from uuid import UUID

from fastapi import APIRouter, status

from src.app.dependencies import OrganizationContext
from src.modules.screening.domain.schemas import (
    ScreeningDocumentReviewCreate,
    ScreeningDocumentReviewResponse,
    ScreeningDocumentUpload,
    ScreeningRequiredDocumentCreate,
    ScreeningRequiredDocumentResponse,
)
from src.modules.screening.presentation.dependencies import (
    ApproveDocumentUC,
    KeepExistingDocumentUC,
    RejectDocumentUC,
    RemoveRequiredDocumentUC,
    ReviewDocumentUC,
    SelectDocumentsUC,
    UploadScreeningDocumentUC,
)

router = APIRouter()


@router.post(
    "/{screening_id}/documents",
    response_model=list[ScreeningRequiredDocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Selecionar documentos",
    description="Seleciona os documentos requeridos para a triagem (Etapa 2)",
)
async def select_documents(
    screening_id: UUID,
    documents: list[ScreeningRequiredDocumentCreate],
    ctx: OrganizationContext,
    use_case: SelectDocumentsUC,
) -> list[ScreeningRequiredDocumentResponse]:
    """Select required documents for the screening."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        documents=documents,
        updated_by=ctx.user,
    )


@router.delete(
    "/{screening_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover documento requerido",
    description="Remove um documento da lista de requeridos",
)
async def remove_required_document(
    screening_id: UUID,
    document_id: UUID,
    ctx: OrganizationContext,
    use_case: RemoveRequiredDocumentUC,
) -> None:
    """Remove a required document."""
    await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        document_id=document_id,
    )


@router.post(
    "/{screening_id}/documents/{document_id}/upload",
    response_model=ScreeningRequiredDocumentResponse,
    summary="Upload de documento",
    description="Faz upload de um documento para a triagem (Etapa 3)",
)
async def upload_document(
    screening_id: UUID,
    document_id: UUID,
    data: ScreeningDocumentUpload,
    ctx: OrganizationContext,
    use_case: UploadScreeningDocumentUC,
) -> ScreeningRequiredDocumentResponse:
    """Upload a document for the screening."""
    return await use_case.execute(
        screening_id=screening_id,
        required_document_id=document_id,
        data=data,
        uploaded_by=ctx.user,
    )


@router.post(
    "/{screening_id}/documents/{document_id}/keep",
    response_model=ScreeningRequiredDocumentResponse,
    summary="Manter documento existente",
    description="Mantém um documento existente do profissional",
)
async def keep_existing_document(
    screening_id: UUID,
    document_id: UUID,
    professional_document_id: UUID,
    ctx: OrganizationContext,
    use_case: KeepExistingDocumentUC,
) -> ScreeningRequiredDocumentResponse:
    """Keep an existing professional document."""
    return await use_case.execute(
        screening_id=screening_id,
        required_document_id=document_id,
        professional_document_id=professional_document_id,
        updated_by=ctx.user,
    )


@router.post(
    "/{screening_id}/documents/{document_id}/review",
    response_model=ScreeningDocumentReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Revisar documento",
    description="Cria uma revisão de documento (Etapa 4)",
)
async def review_document(
    screening_id: UUID,
    document_id: UUID,
    data: ScreeningDocumentReviewCreate,
    ctx: OrganizationContext,
    use_case: ReviewDocumentUC,
) -> ScreeningDocumentReviewResponse:
    """Review a screening document."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        required_document_id=document_id,
        data=data,
        reviewed_by=ctx.user,
    )


@router.post(
    "/{screening_id}/documents/{document_id}/approve",
    response_model=ScreeningDocumentReviewResponse,
    summary="Aprovar documento",
    description="Aprova um documento",
)
async def approve_document(
    screening_id: UUID,
    document_id: UUID,
    ctx: OrganizationContext,
    use_case: ApproveDocumentUC,
    notes: str | None = None,
) -> ScreeningDocumentReviewResponse:
    """Approve a document."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        required_document_id=document_id,
        reviewed_by=ctx.user,
        notes=notes,
    )


@router.post(
    "/{screening_id}/documents/{document_id}/reject",
    response_model=ScreeningDocumentReviewResponse,
    summary="Rejeitar documento",
    description="Rejeita um documento",
)
async def reject_document(
    screening_id: UUID,
    document_id: UUID,
    notes: str,
    ctx: OrganizationContext,
    use_case: RejectDocumentUC,
) -> ScreeningDocumentReviewResponse:
    """Reject a document."""
    return await use_case.execute(
        organization_id=ctx.organization,
        screening_id=screening_id,
        required_document_id=document_id,
        reviewed_by=ctx.user,
        notes=notes,
    )
