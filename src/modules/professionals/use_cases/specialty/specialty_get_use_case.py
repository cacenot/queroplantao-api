"""Use case for retrieving a specialty by ID."""

from uuid import UUID

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
