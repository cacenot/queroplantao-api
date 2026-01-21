"""Use case for retrieving a specialty by code."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import Specialty
from src.modules.professionals.infrastructure.repositories import SpecialtyRepository


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
