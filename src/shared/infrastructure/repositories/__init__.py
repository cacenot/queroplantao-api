"""
Base repository e interfaces compartilhadas.
"""

from src.shared.infrastructure.repositories.base import BaseRepository
from src.shared.infrastructure.repositories.document_type_repository import (
    DocumentTypeRepository,
)
from src.shared.infrastructure.repositories.mixins import SoftDeleteMixin
from src.shared.infrastructure.repositories.organization_scope_mixin import (
    OrganizationScopeMixin,
    ScopePolicy,
)
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)

__all__ = [
    "BaseRepository",
    "SoftDeleteMixin",
    "OrganizationScopeMixin",
    "ScopePolicy",
    # Entity repositories
    "DocumentTypeRepository",
    "SpecialtyRepository",
]
