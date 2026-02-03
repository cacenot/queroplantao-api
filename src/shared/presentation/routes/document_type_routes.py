"""DocumentType routes (organization-scoped, family-visible)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.app.constants.error_codes import DocumentTypeErrorCodes
from src.shared.domain.schemas import (
    DocumentTypeCreate,
    DocumentTypeListResponse,
    DocumentTypeResponse,
    DocumentTypeUpdate,
    ErrorResponse,
)
from src.shared.infrastructure.filters.document_type import (
    DocumentTypeFilter,
    DocumentTypeSorting,
)
from src.shared.presentation.dependencies import (
    CreateDocumentTypeUC,
    DeleteDocumentTypeUC,
    GetDocumentTypeUC,
    ListAllDocumentTypesUC,
    ListDocumentTypesUC,
    OrganizationContext,
    ToggleActiveDocumentTypeUC,
    UpdateDocumentTypeUC,
)


router = APIRouter(prefix="/document-types", tags=["Document Types"])


@router.post(
    "/",
    response_model=DocumentTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create document type",
    description="Create a new document type for the organization.",
)
async def create_document_type(
    data: DocumentTypeCreate,
    ctx: OrganizationContext,
    use_case: CreateDocumentTypeUC,
) -> DocumentTypeResponse:
    """Create a new document type."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        parent_org_id=ctx.parent_org_id,
        family_org_ids=ctx.family_org_ids,
        data=data,
        created_by=ctx.user,
    )
    return DocumentTypeResponse.model_validate(result)


@router.get(
    "/",
    response_model=PaginatedResponse[DocumentTypeListResponse],
    summary="List document types",
    description="List document types with pagination, filtering, and sorting.",
)
async def list_document_types(
    ctx: OrganizationContext,
    use_case: ListDocumentTypesUC,
    pagination: PaginationParams = Depends(),
    filters: DocumentTypeFilter = Depends(filter_as_query(DocumentTypeFilter)),
    sorting: DocumentTypeSorting = Depends(sorting_as_query(DocumentTypeSorting)),
) -> PaginatedResponse[DocumentTypeListResponse]:
    """List document types with pagination."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        family_org_ids=ctx.family_org_ids,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )
    return result  # type: ignore[return-value]


@router.get(
    "/all",
    response_model=list[DocumentTypeListResponse],
    summary="List all document types",
    description="List all document types without pagination. Results are cached for 1 hour.",
)
async def list_all_document_types(
    ctx: OrganizationContext,
    use_case: ListAllDocumentTypesUC,
    filters: DocumentTypeFilter = Depends(filter_as_query(DocumentTypeFilter)),
    sorting: DocumentTypeSorting = Depends(sorting_as_query(DocumentTypeSorting)),
) -> list[DocumentTypeListResponse]:
    """List all document types (cached)."""
    result = await use_case.execute(
        organization_id=ctx.organization,
        parent_org_id=ctx.parent_org_id,
        family_org_ids=ctx.family_org_ids,
        filters=filters,
        sorting=sorting,
    )
    return [DocumentTypeListResponse.model_validate(item) for item in result]


@router.get(
    "/{document_type_id}",
    response_model=DocumentTypeResponse,
    summary="Get document type",
    description="Get a document type by ID.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Document type not found",
                            "value": {
                                "code": DocumentTypeErrorCodes.DOCUMENT_TYPE_NOT_FOUND,
                                "message": "Tipo de documento não encontrado",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def get_document_type(
    document_type_id: UUID,
    ctx: OrganizationContext,
    use_case: GetDocumentTypeUC,
) -> DocumentTypeResponse:
    """Get a document type by ID."""
    result = await use_case.execute(
        document_type_id=document_type_id,
        organization_id=ctx.organization,
        family_org_ids=ctx.family_org_ids,
    )
    return DocumentTypeResponse.model_validate(result)


@router.patch(
    "/{document_type_id}",
    response_model=DocumentTypeResponse,
    summary="Update document type",
    description="Update a document type using PATCH semantics.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Document type not found",
                            "value": {
                                "code": DocumentTypeErrorCodes.DOCUMENT_TYPE_NOT_FOUND,
                                "message": "Tipo de documento não encontrado",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_document_type(
    document_type_id: UUID,
    data: DocumentTypeUpdate,
    ctx: OrganizationContext,
    use_case: UpdateDocumentTypeUC,
) -> DocumentTypeResponse:
    """Update a document type."""
    result = await use_case.execute(
        document_type_id=document_type_id,
        organization_id=ctx.organization,
        parent_org_id=ctx.parent_org_id,
        family_org_ids=ctx.family_org_ids,
        data=data,
        updated_by=ctx.user,
    )
    return DocumentTypeResponse.model_validate(result)


@router.post(
    "/{document_type_id}/activate",
    response_model=DocumentTypeResponse,
    summary="Activate document type",
    description="Activate a document type.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found",
        },
    },
)
async def activate_document_type(
    document_type_id: UUID,
    ctx: OrganizationContext,
    use_case: ToggleActiveDocumentTypeUC,
) -> DocumentTypeResponse:
    """Activate a document type."""
    result = await use_case.execute(
        document_type_id=document_type_id,
        organization_id=ctx.organization,
        parent_org_id=ctx.parent_org_id,
        family_org_ids=ctx.family_org_ids,
        is_active=True,
        updated_by=ctx.user,
    )
    return DocumentTypeResponse.model_validate(result)


@router.post(
    "/{document_type_id}/deactivate",
    response_model=DocumentTypeResponse,
    summary="Deactivate document type",
    description="Deactivate a document type.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found",
        },
    },
)
async def deactivate_document_type(
    document_type_id: UUID,
    ctx: OrganizationContext,
    use_case: ToggleActiveDocumentTypeUC,
) -> DocumentTypeResponse:
    """Deactivate a document type."""
    result = await use_case.execute(
        document_type_id=document_type_id,
        organization_id=ctx.organization,
        parent_org_id=ctx.parent_org_id,
        family_org_ids=ctx.family_org_ids,
        is_active=False,
        updated_by=ctx.user,
    )
    return DocumentTypeResponse.model_validate(result)


@router.delete(
    "/{document_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document type",
    description="Soft delete a document type. Cannot delete if documents are linked.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Document type not found",
                            "value": {
                                "code": DocumentTypeErrorCodes.DOCUMENT_TYPE_NOT_FOUND,
                                "message": "Tipo de documento não encontrado",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict",
            "content": {
                "application/json": {
                    "examples": {
                        "in_use": {
                            "summary": "Document type in use",
                            "value": {
                                "code": DocumentTypeErrorCodes.DOCUMENT_TYPE_IN_USE,
                                "message": "Tipo de documento não pode ser excluído pois está em uso",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def delete_document_type(
    document_type_id: UUID,
    ctx: OrganizationContext,
    use_case: DeleteDocumentTypeUC,
) -> None:
    """Delete a document type."""
    await use_case.execute(
        document_type_id=document_type_id,
        organization_id=ctx.organization,
        parent_org_id=ctx.parent_org_id,
        family_org_ids=ctx.family_org_ids,
    )
