"""Use case for listing organization professionals."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class ListOrganizationProfessionalsUseCase:
    """
    Use case for listing professionals in an organization with pagination.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        is_active: bool | None = None,
    ) -> PaginatedResponse[OrganizationProfessional]:
        """
        List professionals for an organization.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            is_active: Optional filter by active status.

        Returns:
            Paginated list of professionals.
        """
        return await self.repository.list_for_organization(
            organization_id,
            pagination,
            is_active=is_active,
        )
