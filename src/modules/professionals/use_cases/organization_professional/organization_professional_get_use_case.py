"""Use case for getting an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ProfessionalNotFoundError
from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class GetOrganizationProfessionalUseCase:
    """
    Use case for retrieving a single professional from an organization family.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        include_relations: bool = False,
    ) -> OrganizationProfessional:
        """
        Get a professional by ID.

        Args:
            professional_id: The professional UUID.
            organization_id: The organization UUID.
            family_org_ids: List of all organization IDs in the family.
            include_relations: Whether to load related data (qualifications, documents, etc.)

        Returns:
            The professional.

        Raises:
            ProfessionalNotFoundError: If professional not found in organization family.
        """
        if include_relations:
            professional = await self.repository.get_by_id_with_relations(
                id=professional_id,
                organization_id=organization_id,
                family_org_ids=family_org_ids,
            )
        else:
            professional = await self.repository.get_by_id_for_organization(
                id=professional_id,
                organization_id=organization_id,
                family_org_ids=family_org_ids,
            )

        if professional is None:
            raise ProfessionalNotFoundError()

        return professional
