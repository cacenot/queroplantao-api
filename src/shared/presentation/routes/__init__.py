"""Shared routes."""

from src.shared.presentation.routes.enum_routes import router as enum_router
from src.shared.presentation.routes.specialty_routes import router as specialty_router

__all__ = [
    "enum_router",
    "specialty_router",
]
