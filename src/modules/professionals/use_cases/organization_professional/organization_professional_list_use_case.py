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
    Use case for listing professionals in an organization family with pagination.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        filters: OrganizationProfessionalFilter | None = None,
        sorting: OrganizationProfessionalSorting | None = None,
    ) -> PaginatedResponse[OrganizationProfessional]:
        """
        List professionals for an organization family.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            family_org_ids: List of all organization IDs in the family.
            filters: Optional filters (search, gender, marital_status, professional_type).
            sorting: Optional sorting (id, full_name, email, created_at).

        Returns:
            Paginated list of professionals from the entire family.
        """
        return await self.repository.list_for_organization(
            organization_id=organization_id,
            pagination=pagination,
            family_org_ids=family_org_ids,
            filters=filters,
            sorting=sorting,
        )
