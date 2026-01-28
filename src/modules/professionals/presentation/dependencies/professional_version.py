"""Use case factory dependencies for ProfessionalVersion."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.professionals.use_cases.professional_version import (
    ApplyProfessionalVersionUseCase,
    CreateProfessionalVersionUseCase,
    GetProfessionalVersionUseCase,
    ListProfessionalVersionsUseCase,
    RejectProfessionalVersionUseCase,
)


def get_create_professional_version_use_case(
    session: SessionDep,
) -> CreateProfessionalVersionUseCase:
    """Factory for CreateProfessionalVersionUseCase."""
    return CreateProfessionalVersionUseCase(session)


def get_apply_professional_version_use_case(
    session: SessionDep,
) -> ApplyProfessionalVersionUseCase:
    """Factory for ApplyProfessionalVersionUseCase."""
    return ApplyProfessionalVersionUseCase(session)


def get_reject_professional_version_use_case(
    session: SessionDep,
) -> RejectProfessionalVersionUseCase:
    """Factory for RejectProfessionalVersionUseCase."""
    return RejectProfessionalVersionUseCase(session)


def get_professional_version_use_case(
    session: SessionDep,
) -> GetProfessionalVersionUseCase:
    """Factory for GetProfessionalVersionUseCase."""
    return GetProfessionalVersionUseCase(session)


def get_list_professional_versions_use_case(
    session: SessionDep,
) -> ListProfessionalVersionsUseCase:
    """Factory for ListProfessionalVersionsUseCase."""
    return ListProfessionalVersionsUseCase(session)


# Type aliases for cleaner route signatures
CreateProfessionalVersionUC = Annotated[
    CreateProfessionalVersionUseCase,
    Depends(get_create_professional_version_use_case),
]

ApplyProfessionalVersionUC = Annotated[
    ApplyProfessionalVersionUseCase,
    Depends(get_apply_professional_version_use_case),
]

RejectProfessionalVersionUC = Annotated[
    RejectProfessionalVersionUseCase,
    Depends(get_reject_professional_version_use_case),
]

GetProfessionalVersionUC = Annotated[
    GetProfessionalVersionUseCase,
    Depends(get_professional_version_use_case),
]

ListProfessionalVersionsUC = Annotated[
    ListProfessionalVersionsUseCase,
    Depends(get_list_professional_versions_use_case),
]
