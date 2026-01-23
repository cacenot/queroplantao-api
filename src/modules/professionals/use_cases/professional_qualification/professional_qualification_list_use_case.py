"""Use case for listing qualifications for a professional."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ProfessionalNotFoundError
from src.modules.professionals.domain.models import ProfessionalQualification
from src.modules.professionals.infrastructure.filters import (
    ProfessionalQualificationFilter,
    ProfessionalQualificationSorting,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalQualificationRepository,
)


class ListProfessionalQualificationsUseCase:
    """Use case for listing qualifications for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalQualificationFilter | None = None,
        sorting: ProfessionalQualificationSorting | None = None,
    ) -> PaginatedResponse[ProfessionalQualification]:
        """
        List qualifications for a professional.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, professional_type, council_type, etc.).
            sorting: Optional sorting (id, professional_type, council_state, etc.).

        Returns:
            Paginated list of qualifications.
        """
        # Verify professional exists in organization
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        return await self.repository.list_for_professional(
            professional_id,
            pagination,
            filters=filters,
            sorting=sorting,
        )
