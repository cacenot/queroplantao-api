"""
Schemas compartilhados (pagination, common responses, etc).
"""

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams

from src.shared.domain.schemas.bank_account import (
    BankAccountResponse,
    BankInfo,
)
from src.shared.domain.schemas.common import (
    ErrorResponse,
    HealthResponse,
)
from src.shared.domain.schemas.document_type import (
    DocumentTypeCreate,
    DocumentTypeListResponse,
    DocumentTypeResponse,
    DocumentTypeUpdate,
)
from src.shared.domain.schemas.specialty import (
    SpecialtyListResponse,
    SpecialtyResponse,
)

__all__ = [
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "PaginationParams",
    # BankAccount
    "BankAccountResponse",
    "BankInfo",
    # DocumentType
    "DocumentTypeCreate",
    "DocumentTypeListResponse",
    "DocumentTypeResponse",
    "DocumentTypeUpdate",
    # Specialty
    "SpecialtyListResponse",
    "SpecialtyResponse",
]
