"""Use case for retrieving a professional qualification."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import QualificationNotFoundError
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
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        *,
        include_relations: bool = False,
    ) -> ProfessionalQualification:
        """Get a qualification by ID."""
        if include_relations:
            qualification = await self.repository.get_by_id_with_relations(
                qualification_id,
                organization_id,
                family_org_ids=family_org_ids,
            )
        else:
            qualification = await self.repository.get_by_organization(
                id=qualification_id,
                organization_id=organization_id,
                family_org_ids=family_org_ids or (),
            )

        if qualification is None:
            raise QualificationNotFoundError()

        return qualification
