"""Use case factory dependencies for ProfessionalQualification."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.professionals.use_cases import (
    CreateProfessionalQualificationUseCase,
    DeleteProfessionalQualificationUseCase,
    GetProfessionalQualificationUseCase,
    ListProfessionalQualificationsUseCase,
    UpdateProfessionalQualificationUseCase,
)


def get_create_professional_qualification_use_case(
    session: SessionDep,
) -> CreateProfessionalQualificationUseCase:
    """Factory for CreateProfessionalQualificationUseCase."""
    return CreateProfessionalQualificationUseCase(session)


def get_update_professional_qualification_use_case(
    session: SessionDep,
) -> UpdateProfessionalQualificationUseCase:
    """Factory for UpdateProfessionalQualificationUseCase."""
    return UpdateProfessionalQualificationUseCase(session)


def get_delete_professional_qualification_use_case(
    session: SessionDep,
) -> DeleteProfessionalQualificationUseCase:
    """Factory for DeleteProfessionalQualificationUseCase."""
    return DeleteProfessionalQualificationUseCase(session)


def get_professional_qualification_use_case(
    session: SessionDep,
) -> GetProfessionalQualificationUseCase:
    """Factory for GetProfessionalQualificationUseCase."""
    return GetProfessionalQualificationUseCase(session)


def get_list_professional_qualifications_use_case(
    session: SessionDep,
) -> ListProfessionalQualificationsUseCase:
    """Factory for ListProfessionalQualificationsUseCase."""
    return ListProfessionalQualificationsUseCase(session)


# Type aliases for cleaner route signatures
CreateProfessionalQualificationUC = Annotated[
    CreateProfessionalQualificationUseCase,
    Depends(get_create_professional_qualification_use_case),
]
UpdateProfessionalQualificationUC = Annotated[
    UpdateProfessionalQualificationUseCase,
    Depends(get_update_professional_qualification_use_case),
]
DeleteProfessionalQualificationUC = Annotated[
    DeleteProfessionalQualificationUseCase,
    Depends(get_delete_professional_qualification_use_case),
]
GetProfessionalQualificationUC = Annotated[
    GetProfessionalQualificationUseCase,
    Depends(get_professional_qualification_use_case),
]
ListProfessionalQualificationsUC = Annotated[
    ListProfessionalQualificationsUseCase,
    Depends(get_list_professional_qualifications_use_case),
]
