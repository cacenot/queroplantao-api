"""Use case factory dependencies for ProfessionalEducation."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.professionals.use_cases import (
    CreateProfessionalEducationUseCase,
    DeleteProfessionalEducationUseCase,
    GetProfessionalEducationUseCase,
    ListProfessionalEducationsUseCase,
    UpdateProfessionalEducationUseCase,
)


def get_create_professional_education_use_case(
    session: SessionDep,
) -> CreateProfessionalEducationUseCase:
    """Factory for CreateProfessionalEducationUseCase."""
    return CreateProfessionalEducationUseCase(session)


def get_update_professional_education_use_case(
    session: SessionDep,
) -> UpdateProfessionalEducationUseCase:
    """Factory for UpdateProfessionalEducationUseCase."""
    return UpdateProfessionalEducationUseCase(session)


def get_delete_professional_education_use_case(
    session: SessionDep,
) -> DeleteProfessionalEducationUseCase:
    """Factory for DeleteProfessionalEducationUseCase."""
    return DeleteProfessionalEducationUseCase(session)


def get_professional_education_use_case(
    session: SessionDep,
) -> GetProfessionalEducationUseCase:
    """Factory for GetProfessionalEducationUseCase."""
    return GetProfessionalEducationUseCase(session)


def get_list_professional_educations_use_case(
    session: SessionDep,
) -> ListProfessionalEducationsUseCase:
    """Factory for ListProfessionalEducationsUseCase."""
    return ListProfessionalEducationsUseCase(session)


# Type aliases for cleaner route signatures
CreateProfessionalEducationUC = Annotated[
    CreateProfessionalEducationUseCase,
    Depends(get_create_professional_education_use_case),
]
UpdateProfessionalEducationUC = Annotated[
    UpdateProfessionalEducationUseCase,
    Depends(get_update_professional_education_use_case),
]
DeleteProfessionalEducationUC = Annotated[
    DeleteProfessionalEducationUseCase,
    Depends(get_delete_professional_education_use_case),
]
GetProfessionalEducationUC = Annotated[
    GetProfessionalEducationUseCase,
    Depends(get_professional_education_use_case),
]
ListProfessionalEducationsUC = Annotated[
    ListProfessionalEducationsUseCase,
    Depends(get_list_professional_educations_use_case),
]
