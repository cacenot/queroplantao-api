"""ProfessionalSpecialty repository for database operations."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.professionals.domain.models import ProfessionalSpecialty
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeleteMixin,
)


class ProfessionalSpecialtyRepository(
    SoftDeleteMixin[ProfessionalSpecialty],
    BaseRepository[ProfessionalSpecialty],
):
    """
    Repository for ProfessionalSpecialty model.

    Provides CRUD operations with soft delete support.
    """

    model = ProfessionalSpecialty

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_qualification(
        self,
        qualification_id: UUID,
    ) -> Select[tuple[ProfessionalSpecialty]]:
        """
        Get base query filtered by qualification.

        Args:
            qualification_id: The qualification UUID.

        Returns:
            Query filtered by qualification and excluding soft-deleted.
        """
        return self.get_query().where(
            ProfessionalSpecialty.qualification_id == qualification_id
        )

    async def get_by_id_for_qualification(
        self,
        id: UUID,
        qualification_id: UUID,
    ) -> ProfessionalSpecialty | None:
        """
        Get professional specialty by ID for a specific qualification.

        Args:
            id: The professional specialty UUID.
            qualification_id: The qualification UUID.

        Returns:
            Professional specialty if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_qualification(qualification_id).where(
                ProfessionalSpecialty.id == id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_specialty(
        self,
        id: UUID,
        qualification_id: UUID,
    ) -> ProfessionalSpecialty | None:
        """
        Get professional specialty by ID with specialty data loaded.

        Args:
            id: The professional specialty UUID.
            qualification_id: The qualification UUID.

        Returns:
            Professional specialty with specialty loaded.
        """
        result = await self.session.execute(
            self._base_query_for_qualification(qualification_id)
            .where(ProfessionalSpecialty.id == id)
            .options(selectinload(ProfessionalSpecialty.specialty))
        )
        return result.scalar_one_or_none()

    async def get_by_specialty_id(
        self,
        qualification_id: UUID,
        specialty_id: UUID,
    ) -> ProfessionalSpecialty | None:
        """
        Get professional specialty by specialty ID.

        Args:
            qualification_id: The qualification UUID.
            specialty_id: The specialty UUID.

        Returns:
            Professional specialty if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_qualification(qualification_id).where(
                ProfessionalSpecialty.specialty_id == specialty_id
            )
        )
        return result.scalar_one_or_none()

    async def get_primary_specialty(
        self,
        qualification_id: UUID,
    ) -> ProfessionalSpecialty | None:
        """
        Get the primary specialty for a qualification.

        Args:
            qualification_id: The qualification UUID.

        Returns:
            Primary professional specialty if exists, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_qualification(qualification_id)
            .where(ProfessionalSpecialty.is_primary.is_(True))
            .options(selectinload(ProfessionalSpecialty.specialty))
        )
        return result.scalar_one_or_none()

    async def specialty_exists_for_qualification(
        self,
        qualification_id: UUID,
        specialty_id: UUID,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a specialty already exists for the qualification.

        Args:
            qualification_id: The qualification UUID.
            specialty_id: The specialty UUID.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if specialty exists, False otherwise.
        """
        query = self._base_query_for_qualification(qualification_id).where(
            ProfessionalSpecialty.specialty_id == specialty_id
        )
        if exclude_id:
            query = query.where(ProfessionalSpecialty.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()
