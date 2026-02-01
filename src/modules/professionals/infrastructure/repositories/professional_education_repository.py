"""ProfessionalEducation repository for database operations."""

from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import ProfessionalEducation
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeleteMixin,
)


class ProfessionalEducationRepository(
    SoftDeleteMixin[ProfessionalEducation],
    BaseRepository[ProfessionalEducation],
):
    """
    Repository for ProfessionalEducation model.

    Provides CRUD operations with soft delete support.
    """

    model = ProfessionalEducation

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_qualification(
        self,
        qualification_id: UUID,
    ) -> Select[tuple[ProfessionalEducation]]:
        """
        Get base query filtered by qualification.

        Args:
            qualification_id: The qualification UUID.

        Returns:
            Query filtered by qualification and excluding soft-deleted.
        """
        return self.get_query().where(
            ProfessionalEducation.qualification_id == qualification_id
        )

    async def get_by_id_for_qualification(
        self,
        id: UUID,
        qualification_id: UUID,
    ) -> ProfessionalEducation | None:
        """
        Get education by ID for a specific qualification.

        Args:
            id: The education UUID.
            qualification_id: The qualification UUID.

        Returns:
            Education if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_qualification(qualification_id).where(
                ProfessionalEducation.id == id
            )
        )
        return result.scalar_one_or_none()
