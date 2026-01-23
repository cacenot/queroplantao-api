"""Use case for listing organization professionals."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.infrastructure.filters import (
    OrganizationProfessionalFilter,
    OrganizationProfessionalSorting,
)
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
        filters: OrganizationProfessionalFilter | None = None,
        sorting: OrganizationProfessionalSorting | None = None,
    ) -> PaginatedResponse[OrganizationProfessional]:
        """
        List professionals for an organization.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, gender, marital_status, professional_type).
            sorting: Optional sorting (id, full_name, email, created_at).

        Returns:
            Paginated list of professionals.
        """
        return await self.repository.list_for_organization(
            organization_id,
            pagination,
            filters=filters,
            sorting=sorting,
        )
