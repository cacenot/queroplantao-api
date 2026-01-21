"""Use case factory dependencies for OrganizationProfessional."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.professionals.use_cases import (
    CreateOrganizationProfessionalUseCase,
    DeleteOrganizationProfessionalUseCase,
    GetOrganizationProfessionalUseCase,
    ListOrganizationProfessionalsUseCase,
    UpdateOrganizationProfessionalUseCase,
)


def get_create_organization_professional_use_case(
    session: SessionDep,
) -> CreateOrganizationProfessionalUseCase:
    """Factory for CreateOrganizationProfessionalUseCase."""
    return CreateOrganizationProfessionalUseCase(session)


def get_update_organization_professional_use_case(
    session: SessionDep,
) -> UpdateOrganizationProfessionalUseCase:
    """Factory for UpdateOrganizationProfessionalUseCase."""
    return UpdateOrganizationProfessionalUseCase(session)


def get_delete_organization_professional_use_case(
    session: SessionDep,
) -> DeleteOrganizationProfessionalUseCase:
    """Factory for DeleteOrganizationProfessionalUseCase."""
    return DeleteOrganizationProfessionalUseCase(session)


def get_organization_professional_use_case(
    session: SessionDep,
) -> GetOrganizationProfessionalUseCase:
    """Factory for GetOrganizationProfessionalUseCase."""
    return GetOrganizationProfessionalUseCase(session)


def get_list_organization_professionals_use_case(
    session: SessionDep,
) -> ListOrganizationProfessionalsUseCase:
    """Factory for ListOrganizationProfessionalsUseCase."""
    return ListOrganizationProfessionalsUseCase(session)


# Type aliases for cleaner route signatures
CreateOrganizationProfessionalUC = Annotated[
    CreateOrganizationProfessionalUseCase,
    Depends(get_create_organization_professional_use_case),
]
UpdateOrganizationProfessionalUC = Annotated[
    UpdateOrganizationProfessionalUseCase,
    Depends(get_update_organization_professional_use_case),
]
DeleteOrganizationProfessionalUC = Annotated[
    DeleteOrganizationProfessionalUseCase,
    Depends(get_delete_organization_professional_use_case),
]
GetOrganizationProfessionalUC = Annotated[
    GetOrganizationProfessionalUseCase,
    Depends(get_organization_professional_use_case),
]
ListOrganizationProfessionalsUC = Annotated[
    ListOrganizationProfessionalsUseCase,
    Depends(get_list_organization_professionals_use_case),
]
