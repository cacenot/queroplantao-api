"""Use cases for Specialty (read-only for tenants)."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import Specialty
from src.modules.professionals.infrastructure.repositories import SpecialtyRepository


class GetSpecialtyUseCase:
    """Use case for retrieving a specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(self, specialty_id: UUID) -> Specialty:
        """
        Get a specialty by ID.

        Args:
            specialty_id: The specialty UUID.

        Returns:
            The specialty.

        Raises:
            NotFoundError: If specialty not found.
        """
        specialty = await self.repository.get_by_id(specialty_id)
        if specialty is None:
            raise NotFoundError(
                resource="Specialty",
                identifier=str(specialty_id),
            )
        return specialty


class GetSpecialtyByCodeUseCase:
    """Use case for retrieving a specialty by code."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(self, code: str) -> Specialty:
        """
        Get a specialty by code.

        Args:
            code: The specialty code (e.g., 'CARDIOLOGIA').

        Returns:
            The specialty.

        Raises:
            NotFoundError: If specialty not found.
        """
        specialty = await self.repository.get_by_code(code)
        if specialty is None:
            raise NotFoundError(
                resource="Specialty",
                identifier=code,
            )
        return specialty


class ListSpecialtiesUseCase:
    """Use case for listing all specialties."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(
        self,
        pagination: PaginationParams,
    ) -> PaginatedResponse[Specialty]:
        """
        List all active specialties.

        Args:
            pagination: Pagination parameters.

        Returns:
            Paginated list of specialties.
        """
        return await self.repository.list_all(pagination)


class SearchSpecialtiesUseCase:
    """Use case for searching specialties by name."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SpecialtyRepository(session)

    async def execute(
        self,
        name: str,
        pagination: PaginationParams,
    ) -> PaginatedResponse[Specialty]:
        """
        Search specialties by name (case-insensitive partial match).

        Args:
            name: The search term.
            pagination: Pagination parameters.

        Returns:
            Paginated list of matching specialties.
        """
        return await self.repository.search_by_name(name, pagination)
