"""Use case factory dependencies for DocumentType."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.shared.use_cases import (
    CreateDocumentTypeUseCase,
    DeleteDocumentTypeUseCase,
    GetDocumentTypeUseCase,
    ListAllDocumentTypesUseCase,
    ListDocumentTypesUseCase,
    ToggleActiveDocumentTypeUseCase,
    UpdateDocumentTypeUseCase,
)


def get_create_document_type_use_case(
    session: SessionDep,
) -> CreateDocumentTypeUseCase:
    """Factory for CreateDocumentTypeUseCase."""
    return CreateDocumentTypeUseCase(session)


def get_get_document_type_use_case(
    session: SessionDep,
) -> GetDocumentTypeUseCase:
    """Factory for GetDocumentTypeUseCase."""
    return GetDocumentTypeUseCase(session)


def get_update_document_type_use_case(
    session: SessionDep,
) -> UpdateDocumentTypeUseCase:
    """Factory for UpdateDocumentTypeUseCase."""
    return UpdateDocumentTypeUseCase(session)


def get_delete_document_type_use_case(
    session: SessionDep,
) -> DeleteDocumentTypeUseCase:
    """Factory for DeleteDocumentTypeUseCase."""
    return DeleteDocumentTypeUseCase(session)


def get_list_document_types_use_case(
    session: SessionDep,
) -> ListDocumentTypesUseCase:
    """Factory for ListDocumentTypesUseCase."""
    return ListDocumentTypesUseCase(session)


def get_list_all_document_types_use_case(
    session: SessionDep,
) -> ListAllDocumentTypesUseCase:
    """Factory for ListAllDocumentTypesUseCase."""
    return ListAllDocumentTypesUseCase(session)


def get_toggle_active_document_type_use_case(
    session: SessionDep,
) -> ToggleActiveDocumentTypeUseCase:
    """Factory for ToggleActiveDocumentTypeUseCase."""
    return ToggleActiveDocumentTypeUseCase(session)


# Type aliases for cleaner route signatures
CreateDocumentTypeUC = Annotated[
    CreateDocumentTypeUseCase,
    Depends(get_create_document_type_use_case),
]
GetDocumentTypeUC = Annotated[
    GetDocumentTypeUseCase,
    Depends(get_get_document_type_use_case),
]
UpdateDocumentTypeUC = Annotated[
    UpdateDocumentTypeUseCase,
    Depends(get_update_document_type_use_case),
]
DeleteDocumentTypeUC = Annotated[
    DeleteDocumentTypeUseCase,
    Depends(get_delete_document_type_use_case),
]
ListDocumentTypesUC = Annotated[
    ListDocumentTypesUseCase,
    Depends(get_list_document_types_use_case),
]
ListAllDocumentTypesUC = Annotated[
    ListAllDocumentTypesUseCase,
    Depends(get_list_all_document_types_use_case),
]
ToggleActiveDocumentTypeUC = Annotated[
    ToggleActiveDocumentTypeUseCase,
    Depends(get_toggle_active_document_type_use_case),
]
