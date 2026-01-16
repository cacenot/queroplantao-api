"""
Base repository e interfaces compartilhadas.
"""

from src.shared.infrastructure.repositories.base import (
    BaseRepository,
    TenantRepository,
)

__all__ = [
    "BaseRepository",
    "TenantRepository",
]
