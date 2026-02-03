"""Use case for listing professional versions."""

from uuid import UUID

from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ProfessionalNotFoundError
from src.modules.professionals.domain.models.professional_version import (
    ProfessionalVersion,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalVersionFilter,
    ProfessionalVersionSorting,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalVersionRepository,
)


class ListProfessionalVersionsUseCase:
    """Use case for listing professional version history."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.version_repository = ProfessionalVersionRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        professional_id: UUID,
        pagination: PaginationParams,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        *,
        filters: ProfessionalVersionFilter | None = None,
        sorting: ProfessionalVersionSorting | None = None,
    ) -> PaginatedResponse[ProfessionalVersion]:
        """
        List version history for a professional.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID.
            pagination: Pagination parameters.
            family_org_ids: Family org IDs for scope.
            filters: Optional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of versions.

        Raises:
            ProfessionalNotFoundError: If professional doesn't exist.
        """
        # Validate professional exists
        professional = await self.professional_repository.get_by_id_for_organization(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if professional is None:
            raise ProfessionalNotFoundError()

        return await self.version_repository.list_for_professional(
            professional_id=professional_id,
            organization_id=organization_id,
            pagination=pagination,
            filters=filters,
            sorting=sorting,
        )
