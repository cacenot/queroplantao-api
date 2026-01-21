"""
Base repository e interfaces compartilhadas.
"""

from src.shared.infrastructure.repositories.base import BaseRepository
from src.shared.infrastructure.repositories.mixins import (
    PaginationMixin,
    SoftDeleteMixin,
    SoftDeletePaginationMixin,
)
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)

__all__ = [
    "BaseRepository",
    "PaginationMixin",
    "SoftDeleteMixin",
    "SoftDeletePaginationMixin",
    # Entity repositories
    "SpecialtyRepository",
]
