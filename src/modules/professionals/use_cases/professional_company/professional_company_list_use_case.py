"""Use case for listing company links for a professional."""

from uuid import UUID

from fastapi_restkit.filters import ListFilter
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ProfessionalNotFoundError
from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.infrastructure.filters import (
    ProfessionalCompanyFilter,
    ProfessionalCompanySorting,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalCompanyRepository,
)


class ListProfessionalCompaniesUseCase:
    """Use case for listing company links for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalCompanyRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalCompanyFilter | None = None,
        sorting: ProfessionalCompanySorting | None = None,
    ) -> PaginatedResponse[ProfessionalCompany]:
        """
        List company links for a professional.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID.
            pagination: Pagination parameters.
            filters: Optional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of company links.
        """
        # Verify professional exists in organization
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        if filters is None:
            filters = ProfessionalCompanyFilter()

        filters.organization_professional_id = ListFilter(values=[professional_id])

        return await self.repository.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
        )
