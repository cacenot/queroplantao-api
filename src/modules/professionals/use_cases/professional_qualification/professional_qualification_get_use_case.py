"""Use case for retrieving a professional qualification."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalQualification
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
)


class GetProfessionalQualificationUseCase:
    """Use case for retrieving a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        *,
        include_relations: bool = False,
    ) -> ProfessionalQualification:
        """Get a qualification by ID."""
        if include_relations:
            qualification = await self.repository.get_by_id_with_relations(
                qualification_id, organization_id
            )
        else:
            qualification = await self.repository.get_by_id_for_organization(
                qualification_id, organization_id
            )

        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        return qualification
