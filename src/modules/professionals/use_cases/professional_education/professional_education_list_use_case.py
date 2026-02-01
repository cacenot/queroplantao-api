"""Use case for listing education records for a professional."""

from uuid import UUID

from fastapi_restkit.filters import ListFilter
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
from src.modules.professionals.domain.models import ProfessionalEducation
from src.modules.professionals.infrastructure.filters import (
    ProfessionalEducationFilter,
    ProfessionalEducationSorting,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalEducationRepository,
    ProfessionalQualificationRepository,
)


class ListProfessionalEducationsUseCase:
    """Use case for listing education records for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalEducationRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalEducationFilter | None = None,
        sorting: ProfessionalEducationSorting | None = None,
    ) -> PaginatedResponse[ProfessionalEducation]:
        """
        List education records for a professional's primary qualification.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, level, is_completed, is_verified).
            sorting: Optional sorting (id, level, end_year, created_at).

        Returns:
            Paginated list of education records.
        """
        # Verify professional exists in organization
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise NotFoundError(
                resource="OrganizationProfessional",
                identifier=str(professional_id),
            )

        # Get primary qualification
        qualification = await self.qualification_repository.get_primary_qualification(
            professional_id
        )
        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=f"primary for professional {professional_id}",
            )

        if filters is None:
            filters = ProfessionalEducationFilter()

        filters.qualification_id = ListFilter(values=[qualification.id])

        return await self.repository.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
        )
