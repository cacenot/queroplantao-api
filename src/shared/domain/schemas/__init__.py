"""
Schemas compartilhados (pagination, common responses, etc).
"""

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams

from src.shared.domain.schemas.common import (
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "PaginationParams",
]
