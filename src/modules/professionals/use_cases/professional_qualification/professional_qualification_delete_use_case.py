"""Use case for soft-deleting a professional qualification."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
)


class DeleteProfessionalQualificationUseCase:
    """Use case for soft-deleting a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
    ) -> None:
        """Soft delete a qualification."""
        qualification = await self.repository.get_by_id_for_organization(
            qualification_id, organization_id
        )
        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        await self.repository.soft_delete(qualification_id)
