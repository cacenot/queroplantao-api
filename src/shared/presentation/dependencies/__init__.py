"""Shared presentation dependencies."""

from src.app.dependencies.context import CurrentContext, OrganizationContext
from src.shared.presentation.dependencies.document_type import (
    CreateDocumentTypeUC,
    DeleteDocumentTypeUC,
    GetDocumentTypeUC,
    ListAllDocumentTypesUC,
    ListDocumentTypesUC,
    ToggleActiveDocumentTypeUC,
    UpdateDocumentTypeUC,
    get_create_document_type_use_case,
    get_delete_document_type_use_case,
    get_get_document_type_use_case,
    get_list_all_document_types_use_case,
    get_list_document_types_use_case,
    get_toggle_active_document_type_use_case,
    get_update_document_type_use_case,
)
from src.shared.presentation.dependencies.specialty import (
    GetSpecialtyByCodeUC,
    GetSpecialtyUC,
    ListSpecialtiesUC,
    SearchSpecialtiesUC,
    get_list_specialties_use_case,
    get_search_specialties_use_case,
    get_specialty_by_code_use_case,
    get_specialty_use_case,
)

__all__ = [
    # Context
    "CurrentContext",
    "OrganizationContext",
    # DocumentType use cases
    "CreateDocumentTypeUC",
    "DeleteDocumentTypeUC",
    "GetDocumentTypeUC",
    "ListAllDocumentTypesUC",
    "ListDocumentTypesUC",
    "ToggleActiveDocumentTypeUC",
    "UpdateDocumentTypeUC",
    "get_create_document_type_use_case",
    "get_delete_document_type_use_case",
    "get_get_document_type_use_case",
    "get_list_all_document_types_use_case",
    "get_list_document_types_use_case",
    "get_toggle_active_document_type_use_case",
    "get_update_document_type_use_case",
    # Specialty use cases
    "GetSpecialtyByCodeUC",
    "GetSpecialtyUC",
    "ListSpecialtiesUC",
    "SearchSpecialtiesUC",
    "get_list_specialties_use_case",
    "get_search_specialties_use_case",
    "get_specialty_by_code_use_case",
    "get_specialty_use_case",
]
