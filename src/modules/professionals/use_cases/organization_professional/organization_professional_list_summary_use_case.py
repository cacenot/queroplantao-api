"""Use case for listing organization professionals with summary data."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.schemas import (
    OrganizationProfessionalListItem,
    QualificationSummary,
    SpecialtySummary,
)
from src.modules.professionals.infrastructure.filters import (
    OrganizationProfessionalFilter,
    OrganizationProfessionalSorting,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class ListOrganizationProfessionalsSummaryUseCase:
    """
    Use case for listing professionals with simplified summary data.

    Returns a lighter response format with:
    - Basic professional info (id, name, avatar, contact, location)
    - Primary qualification summary (type, council info)
    - List of specialties (id, name only)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    def _build_list_item(
        self, professional: OrganizationProfessional
    ) -> OrganizationProfessionalListItem:
        """
        Build a simplified list item from a professional with loaded relations.

        Args:
            professional: The professional with primary qualification and specialties loaded.
                          Only the primary qualification (is_primary=True) is loaded by the
                          repository, already filtered by deleted_at IS NULL.

        Returns:
            Simplified list item schema.
        """
        qualification_summary: QualificationSummary | None = None
        specialties: list[SpecialtySummary] = []

        # Repository loads only primary qualification (is_primary=True, deleted_at IS NULL)
        if professional.qualifications:
            primary_qual = professional.qualifications[0]

            qualification_summary = QualificationSummary(
                professional_type=primary_qual.professional_type.value,
                council_type=primary_qual.council_type.value,
                council_number=primary_qual.council_number,
                council_state=primary_qual.council_state,
            )

            # Collect specialties from primary qualification (pre-filtered by repository)
            for ps in primary_qual.specialties:
                if ps.specialty:
                    specialties.append(
                        SpecialtySummary(
                            id=ps.specialty.id,
                            name=ps.specialty.name,
                        )
                    )

        return OrganizationProfessionalListItem(
            id=professional.id,
            avatar_url=professional.avatar_url,
            full_name=professional.full_name,
            city=professional.city,
            state_code=professional.state_code,
            cpf=professional.cpf,
            phone=professional.phone,
            email=professional.email,
            qualification=qualification_summary,
            specialties=specialties,
        )

    async def execute(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        filters: OrganizationProfessionalFilter | None = None,
        sorting: OrganizationProfessionalSorting | None = None,
    ) -> PaginatedResponse[OrganizationProfessionalListItem]:
        """
        List professionals with summary data for an organization.

        Args:
            organization_id: The organization UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, gender, marital_status, professional_type).
            sorting: Optional sorting (id, full_name, email, created_at).

        Returns:
            Paginated list of professional summaries.
        """
        result = await self.repository.list_for_organization_with_summary(
            organization_id,
            pagination,
            filters=filters,
            sorting=sorting,
        )

        # Transform items to list item schema
        items = [self._build_list_item(p) for p in result.items]

        return PaginatedResponse(
            items=items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
            has_next=result.has_next,
            has_previous=result.has_previous,
        )
