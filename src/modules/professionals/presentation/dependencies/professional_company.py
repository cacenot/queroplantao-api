"""Use case factory dependencies for ProfessionalCompany."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.professionals.use_cases import (
    CreateProfessionalCompanyUseCase,
    DeleteProfessionalCompanyUseCase,
    GetProfessionalCompanyUseCase,
    ListProfessionalCompaniesUseCase,
    UpdateProfessionalCompanyUseCase,
)


def get_create_professional_company_use_case(
    session: SessionDep,
) -> CreateProfessionalCompanyUseCase:
    """Factory for CreateProfessionalCompanyUseCase."""
    return CreateProfessionalCompanyUseCase(session)


def get_update_professional_company_use_case(
    session: SessionDep,
) -> UpdateProfessionalCompanyUseCase:
    """Factory for UpdateProfessionalCompanyUseCase."""
    return UpdateProfessionalCompanyUseCase(session)


def get_delete_professional_company_use_case(
    session: SessionDep,
) -> DeleteProfessionalCompanyUseCase:
    """Factory for DeleteProfessionalCompanyUseCase."""
    return DeleteProfessionalCompanyUseCase(session)


def get_professional_company_use_case(
    session: SessionDep,
) -> GetProfessionalCompanyUseCase:
    """Factory for GetProfessionalCompanyUseCase."""
    return GetProfessionalCompanyUseCase(session)


def get_list_professional_companies_use_case(
    session: SessionDep,
) -> ListProfessionalCompaniesUseCase:
    """Factory for ListProfessionalCompaniesUseCase."""
    return ListProfessionalCompaniesUseCase(session)


# Type aliases for cleaner route signatures
CreateProfessionalCompanyUC = Annotated[
    CreateProfessionalCompanyUseCase,
    Depends(get_create_professional_company_use_case),
]
UpdateProfessionalCompanyUC = Annotated[
    UpdateProfessionalCompanyUseCase,
    Depends(get_update_professional_company_use_case),
]
DeleteProfessionalCompanyUC = Annotated[
    DeleteProfessionalCompanyUseCase,
    Depends(get_delete_professional_company_use_case),
]
GetProfessionalCompanyUC = Annotated[
    GetProfessionalCompanyUseCase,
    Depends(get_professional_company_use_case),
]
ListProfessionalCompaniesUC = Annotated[
    ListProfessionalCompaniesUseCase,
    Depends(get_list_professional_companies_use_case),
]
