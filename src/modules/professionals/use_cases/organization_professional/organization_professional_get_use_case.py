"""Use case for getting an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class GetOrganizationProfessionalUseCase:
    """
    Use case for retrieving a single professional from an organization.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        *,
        include_relations: bool = False,
    ) -> OrganizationProfessional:
        """
        Get a professional by ID.

        Args:
            professional_id: The professional UUID.
            organization_id: The organization UUID.
            include_relations: Whether to load related data (qualifications, documents, etc.)

        Returns:
            The professional.

        Raises:
            NotFoundError: If professional not found in organization.
        """
        if include_relations:
            professional = await self.repository.get_by_id_with_relations(
                professional_id, organization_id
            )
        else:
            professional = await self.repository.get_by_id_for_organization(
                professional_id, organization_id
            )

        if professional is None:
            raise NotFoundError(
                resource="OrganizationProfessional",
                identifier=str(professional_id),
            )

        return professional
