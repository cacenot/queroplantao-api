"""Use case for listing specialties for a professional."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ProfessionalNotFoundError, QualificationNotFoundError
from src.modules.professionals.domain.models import ProfessionalSpecialty
from src.modules.professionals.infrastructure.filters import (
    ProfessionalSpecialtyFilter,
    ProfessionalSpecialtySorting,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
)


class ListProfessionalSpecialtiesUseCase:
    """Use case for listing specialties for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalSpecialtyFilter | None = None,
        sorting: ProfessionalSpecialtySorting | None = None,
    ) -> PaginatedResponse[ProfessionalSpecialty]:
        """
        List specialties for a professional's primary qualification.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search by RQE, is_verified).
            sorting: Optional sorting (id, acquisition_date, created_at).

        Returns:
            Paginated list of specialties.
        """
        # Verify professional exists in organization
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # Get primary qualification
        qualification = await self.qualification_repository.get_primary_qualification(
            professional_id
        )
        if qualification is None:
            raise QualificationNotFoundError()

        return await self.repository.list_for_qualification(
            qualification.id,
            pagination,
            filters=filters,
            sorting=sorting,
        )
