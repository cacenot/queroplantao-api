"""Shared presentation layer."""

from src.shared.presentation.routes import (
    document_type_router,
    enum_router,
    specialty_router,
)

__all__ = [
    "document_type_router",
    "enum_router",
    "specialty_router",
]
