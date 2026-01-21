"""Professional Document routes (nested under professionals)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.modules.professionals.domain.schemas import (
    ProfessionalDocumentCreate,
    ProfessionalDocumentResponse,
    ProfessionalDocumentUpdate,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalDocumentFilter,
    ProfessionalDocumentSorting,
)
from src.modules.professionals.presentation.dependencies import (
    CreateProfessionalDocumentUC,
    DeleteProfessionalDocumentUC,
    GetProfessionalDocumentUC,
    ListProfessionalDocumentsUC,
    OrganizationContext,
    UpdateProfessionalDocumentUC,
)


router = APIRouter(
    prefix="/professionals/{professional_id}/documents",
    tags=["Professional Documents"],
)


@router.post(
    "/",
    response_model=ProfessionalDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a document to a professional",
    description="Create a new document for a professional.",
)
async def create_document(
    professional_id: UUID,
    data: ProfessionalDocumentCreate,
    ctx: OrganizationContext,
    use_case: CreateProfessionalDocumentUC,
) -> ProfessionalDocumentResponse:
    """Create a new document for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        data=data,
        created_by=ctx.user,
    )
    return ProfessionalDocumentResponse.model_validate(result)


@router.get(
    "/",
    response_model=PaginatedResponse[ProfessionalDocumentResponse],
    summary="List professional documents",
    description="List all documents for a professional with pagination, filtering and sorting.",
)
async def list_documents(
    professional_id: UUID,
    ctx: OrganizationContext,
    use_case: ListProfessionalDocumentsUC,
    pagination: PaginationParams = Depends(),
    filters: ProfessionalDocumentFilter = Depends(
        filter_as_query(ProfessionalDocumentFilter)
    ),
    sorting: ProfessionalDocumentSorting = Depends(
        sorting_as_query(ProfessionalDocumentSorting)
    ),
) -> PaginatedResponse[ProfessionalDocumentResponse]:
    """List all documents for a professional."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result


@router.get(
    "/{document_id}",
    response_model=ProfessionalDocumentResponse,
    summary="Get a professional document",
    description="Get a specific document by ID.",
)
async def get_document(
    professional_id: UUID,
    document_id: UUID,
    ctx: OrganizationContext,
    use_case: GetProfessionalDocumentUC,
) -> ProfessionalDocumentResponse:
    """Get a document by ID."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        document_id=document_id,
    )
    return ProfessionalDocumentResponse.model_validate(result)


@router.patch(
    "/{document_id}",
    response_model=ProfessionalDocumentResponse,
    summary="Update a professional document",
    description="Partially update a document. Only provided fields will be updated.",
)
async def update_document(
    professional_id: UUID,
    document_id: UUID,
    data: ProfessionalDocumentUpdate,
    ctx: OrganizationContext,
    use_case: UpdateProfessionalDocumentUC,
) -> ProfessionalDocumentResponse:
    """Update a document."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        document_id=document_id,
        data=data,
        updated_by=ctx.user,
    )
    return ProfessionalDocumentResponse.model_validate(result)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a professional document",
    description="Soft delete a document.",
)
async def delete_document(
    professional_id: UUID,
    document_id: UUID,
    ctx: OrganizationContext,
    use_case: DeleteProfessionalDocumentUC,
) -> None:
    """Soft delete a document."""
    await use_case.execute(
        organization_id=ctx.organization,
        professional_id=professional_id,
        document_id=document_id,
        deleted_by=ctx.user,
    )
