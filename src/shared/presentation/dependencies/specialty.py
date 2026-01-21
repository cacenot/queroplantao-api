"""Use case factory dependencies for Specialty (global, read-only)."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.shared.use_cases import (
    GetSpecialtyByCodeUseCase,
    GetSpecialtyUseCase,
    ListSpecialtiesUseCase,
    SearchSpecialtiesUseCase,
)


def get_specialty_use_case(
    session: SessionDep,
) -> GetSpecialtyUseCase:
    """Factory for GetSpecialtyUseCase."""
    return GetSpecialtyUseCase(session)


def get_specialty_by_code_use_case(
    session: SessionDep,
) -> GetSpecialtyByCodeUseCase:
    """Factory for GetSpecialtyByCodeUseCase."""
    return GetSpecialtyByCodeUseCase(session)


def get_list_specialties_use_case(
    session: SessionDep,
) -> ListSpecialtiesUseCase:
    """Factory for ListSpecialtiesUseCase."""
    return ListSpecialtiesUseCase(session)


def get_search_specialties_use_case(
    session: SessionDep,
) -> SearchSpecialtiesUseCase:
    """Factory for SearchSpecialtiesUseCase."""
    return SearchSpecialtiesUseCase(session)


# Type aliases for cleaner route signatures
GetSpecialtyUC = Annotated[
    GetSpecialtyUseCase,
    Depends(get_specialty_use_case),
]
GetSpecialtyByCodeUC = Annotated[
    GetSpecialtyByCodeUseCase,
    Depends(get_specialty_by_code_use_case),
]
ListSpecialtiesUC = Annotated[
    ListSpecialtiesUseCase,
    Depends(get_list_specialties_use_case),
]
SearchSpecialtiesUC = Annotated[
    SearchSpecialtiesUseCase,
    Depends(get_search_specialties_use_case),
]
