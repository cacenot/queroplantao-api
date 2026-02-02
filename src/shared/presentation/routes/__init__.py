"""Shared routes."""

from src.shared.presentation.routes.document_type_routes import (
    router as document_type_router,
)
from src.shared.presentation.routes.enum_routes import router as enum_router
from src.shared.presentation.routes.specialty_routes import router as specialty_router

__all__ = [
    "document_type_router",
    "enum_router",
    "specialty_router",
]
