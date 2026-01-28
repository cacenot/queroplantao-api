"""
Use cases for professional versioning.

Provides version history management for professionals:
- Create versions with snapshots
- Apply pending versions
- Reject pending versions
- Get and list versions
"""

from src.modules.professionals.use_cases.professional_version.professional_version_apply_use_case import (
    ApplyProfessionalVersionUseCase,
)
from src.modules.professionals.use_cases.professional_version.professional_version_create_use_case import (
    CreateProfessionalVersionUseCase,
)
from src.modules.professionals.use_cases.professional_version.professional_version_get_use_case import (
    GetProfessionalVersionUseCase,
)
from src.modules.professionals.use_cases.professional_version.professional_version_list_use_case import (
    ListProfessionalVersionsUseCase,
)
from src.modules.professionals.use_cases.professional_version.professional_version_reject_use_case import (
    RejectProfessionalVersionUseCase,
)
from src.modules.professionals.use_cases.professional_version.services import (
    DiffCalculatorService,
    SnapshotApplierService,
    SnapshotBuilderService,
)

__all__ = [
    # Use cases
    "CreateProfessionalVersionUseCase",
    "ApplyProfessionalVersionUseCase",
    "RejectProfessionalVersionUseCase",
    "GetProfessionalVersionUseCase",
    "ListProfessionalVersionsUseCase",
    # Services
    "DiffCalculatorService",
    "SnapshotApplierService",
    "SnapshotBuilderService",
]
