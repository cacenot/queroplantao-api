"""Shared use cases."""

from src.shared.use_cases.document_type import (
    CreateDocumentTypeUseCase,
    DeleteDocumentTypeUseCase,
    GetDocumentTypeUseCase,
    ListAllDocumentTypesUseCase,
    ListDocumentTypesUseCase,
    ToggleActiveDocumentTypeUseCase,
    UpdateDocumentTypeUseCase,
)
from src.shared.use_cases.specialty import (
    GetSpecialtyByCodeUseCase,
    GetSpecialtyUseCase,
    ListSpecialtiesUseCase,
    SearchSpecialtiesUseCase,
)

__all__ = [
    # DocumentType
    "CreateDocumentTypeUseCase",
    "DeleteDocumentTypeUseCase",
    "GetDocumentTypeUseCase",
    "ListAllDocumentTypesUseCase",
    "ListDocumentTypesUseCase",
    "ToggleActiveDocumentTypeUseCase",
    "UpdateDocumentTypeUseCase",
    # Specialty
    "GetSpecialtyByCodeUseCase",
    "GetSpecialtyUseCase",
    "ListSpecialtiesUseCase",
    "SearchSpecialtiesUseCase",
]
