"""DocumentType use cases."""

from src.shared.use_cases.document_type.document_type_create_use_case import (
    CreateDocumentTypeUseCase,
)
from src.shared.use_cases.document_type.document_type_delete_use_case import (
    DeleteDocumentTypeUseCase,
)
from src.shared.use_cases.document_type.document_type_get_use_case import (
    GetDocumentTypeUseCase,
)
from src.shared.use_cases.document_type.document_type_list_all_use_case import (
    ListAllDocumentTypesUseCase,
)
from src.shared.use_cases.document_type.document_type_list_use_case import (
    ListDocumentTypesUseCase,
)
from src.shared.use_cases.document_type.document_type_toggle_active_use_case import (
    ToggleActiveDocumentTypeUseCase,
)
from src.shared.use_cases.document_type.document_type_update_use_case import (
    UpdateDocumentTypeUseCase,
)

__all__ = [
    "CreateDocumentTypeUseCase",
    "DeleteDocumentTypeUseCase",
    "GetDocumentTypeUseCase",
    "ListAllDocumentTypesUseCase",
    "ListDocumentTypesUseCase",
    "ToggleActiveDocumentTypeUseCase",
    "UpdateDocumentTypeUseCase",
]
