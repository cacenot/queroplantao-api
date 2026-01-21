"""Use case factory dependencies for ProfessionalDocument."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.professionals.use_cases import (
    CreateProfessionalDocumentUseCase,
    DeleteProfessionalDocumentUseCase,
    GetProfessionalDocumentUseCase,
    ListProfessionalDocumentsUseCase,
    UpdateProfessionalDocumentUseCase,
)


def get_create_professional_document_use_case(
    session: SessionDep,
) -> CreateProfessionalDocumentUseCase:
    """Factory for CreateProfessionalDocumentUseCase."""
    return CreateProfessionalDocumentUseCase(session)


def get_update_professional_document_use_case(
    session: SessionDep,
) -> UpdateProfessionalDocumentUseCase:
    """Factory for UpdateProfessionalDocumentUseCase."""
    return UpdateProfessionalDocumentUseCase(session)


def get_delete_professional_document_use_case(
    session: SessionDep,
) -> DeleteProfessionalDocumentUseCase:
    """Factory for DeleteProfessionalDocumentUseCase."""
    return DeleteProfessionalDocumentUseCase(session)


def get_professional_document_use_case(
    session: SessionDep,
) -> GetProfessionalDocumentUseCase:
    """Factory for GetProfessionalDocumentUseCase."""
    return GetProfessionalDocumentUseCase(session)


def get_list_professional_documents_use_case(
    session: SessionDep,
) -> ListProfessionalDocumentsUseCase:
    """Factory for ListProfessionalDocumentsUseCase."""
    return ListProfessionalDocumentsUseCase(session)


# Type aliases for cleaner route signatures
CreateProfessionalDocumentUC = Annotated[
    CreateProfessionalDocumentUseCase,
    Depends(get_create_professional_document_use_case),
]
UpdateProfessionalDocumentUC = Annotated[
    UpdateProfessionalDocumentUseCase,
    Depends(get_update_professional_document_use_case),
]
DeleteProfessionalDocumentUC = Annotated[
    DeleteProfessionalDocumentUseCase,
    Depends(get_delete_professional_document_use_case),
]
GetProfessionalDocumentUC = Annotated[
    GetProfessionalDocumentUseCase,
    Depends(get_professional_document_use_case),
]
ListProfessionalDocumentsUC = Annotated[
    ListProfessionalDocumentsUseCase,
    Depends(get_list_professional_documents_use_case),
]
