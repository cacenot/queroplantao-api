"""Use case factory dependencies for ProfessionalSpecialty."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.professionals.use_cases import (
    CreateProfessionalSpecialtyUseCase,
    DeleteProfessionalSpecialtyUseCase,
    GetProfessionalSpecialtyUseCase,
    ListProfessionalSpecialtiesUseCase,
    UpdateProfessionalSpecialtyUseCase,
)


def get_create_professional_specialty_use_case(
    session: SessionDep,
) -> CreateProfessionalSpecialtyUseCase:
    """Factory for CreateProfessionalSpecialtyUseCase."""
    return CreateProfessionalSpecialtyUseCase(session)


def get_update_professional_specialty_use_case(
    session: SessionDep,
) -> UpdateProfessionalSpecialtyUseCase:
    """Factory for UpdateProfessionalSpecialtyUseCase."""
    return UpdateProfessionalSpecialtyUseCase(session)


def get_delete_professional_specialty_use_case(
    session: SessionDep,
) -> DeleteProfessionalSpecialtyUseCase:
    """Factory for DeleteProfessionalSpecialtyUseCase."""
    return DeleteProfessionalSpecialtyUseCase(session)


def get_professional_specialty_use_case(
    session: SessionDep,
) -> GetProfessionalSpecialtyUseCase:
    """Factory for GetProfessionalSpecialtyUseCase."""
    return GetProfessionalSpecialtyUseCase(session)


def get_list_professional_specialties_use_case(
    session: SessionDep,
) -> ListProfessionalSpecialtiesUseCase:
    """Factory for ListProfessionalSpecialtiesUseCase."""
    return ListProfessionalSpecialtiesUseCase(session)


# Type aliases for cleaner route signatures
CreateProfessionalSpecialtyUC = Annotated[
    CreateProfessionalSpecialtyUseCase,
    Depends(get_create_professional_specialty_use_case),
]
UpdateProfessionalSpecialtyUC = Annotated[
    UpdateProfessionalSpecialtyUseCase,
    Depends(get_update_professional_specialty_use_case),
]
DeleteProfessionalSpecialtyUC = Annotated[
    DeleteProfessionalSpecialtyUseCase,
    Depends(get_delete_professional_specialty_use_case),
]
GetProfessionalSpecialtyUC = Annotated[
    GetProfessionalSpecialtyUseCase,
    Depends(get_professional_specialty_use_case),
]
ListProfessionalSpecialtiesUC = Annotated[
    ListProfessionalSpecialtiesUseCase,
    Depends(get_list_professional_specialties_use_case),
]
