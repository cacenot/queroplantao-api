"""ProfessionalQualification repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.professionals.domain.models import (
    CouncilType,
    ProfessionalQualification,
    ProfessionalType,
)
from src.modules.professionals.infrastructure.filters import (
    ProfessionalQualificationFilter,
    ProfessionalQualificationSorting,
)
from src.shared.infrastructure.repositories import (
    BaseRepository,
    OrganizationScopeMixin,
    ScopePolicy,
    SoftDeleteMixin,
)


class ProfessionalQualificationRepository(
    OrganizationScopeMixin[ProfessionalQualification],
    SoftDeleteMixin[ProfessionalQualification],
    BaseRepository[ProfessionalQualification],
):
    """
    Repository for ProfessionalQualification model.

    Provides CRUD operations with soft delete support and multi-tenancy filtering.
    """

    model = ProfessionalQualification
    default_scope_policy: ScopePolicy = "ORGANIZATION_ONLY"

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_professional(
        self,
        professional_id: UUID,
    ) -> Select[tuple[ProfessionalQualification]]:
        """
        Get base query filtered by professional.

        Args:
            professional_id: The organization professional UUID.

        Returns:
            Query filtered by professional and excluding soft-deleted.
        """
        return self.get_query().where(
            ProfessionalQualification.organization_professional_id == professional_id
        )

    async def get_by_id_with_relations(
        self,
        id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        scope_policy: ScopePolicy | None = None,
    ) -> ProfessionalQualification | None:
        """
        Get qualification by ID with related data loaded.

        Args:
            id: The qualification UUID.
            organization_id: The organization UUID.

        Returns:
            Qualification with specialties, educations, documents loaded.
        """
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = (
            super()
            .get_query()
            .options(
                selectinload(ProfessionalQualification.specialties),
                selectinload(ProfessionalQualification.educations),
                selectinload(ProfessionalQualification.documents),
            )
        )
        base_query = self._apply_org_scope(base_query, org_ids)
        result = await self.session.execute(
            base_query.where(ProfessionalQualification.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_professional_type(
        self,
        professional_id: UUID,
        professional_type: ProfessionalType,
    ) -> ProfessionalQualification | None:
        """
        Get qualification by professional type.

        Args:
            professional_id: The organization professional UUID.
            professional_type: The professional type (DOCTOR, NURSE, etc.).

        Returns:
            Qualification if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id).where(
                ProfessionalQualification.professional_type == professional_type
            )
        )
        return result.scalar_one_or_none()

    async def get_primary_qualification(
        self,
        professional_id: UUID,
    ) -> ProfessionalQualification | None:
        """
        Get the primary qualification for a professional.

        Args:
            professional_id: The organization professional UUID.

        Returns:
            Primary qualification if exists, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id).where(
                ProfessionalQualification.is_primary.is_(True)
            )
        )
        return result.scalar_one_or_none()

    async def council_exists_in_organization(
        self,
        council_number: str,
        council_state: str,
        organization_id: UUID,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a council registration already exists in the organization.

        Args:
            council_number: The council registration number.
            council_state: The council state (2 chars).
            organization_id: The organization UUID.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if council exists, False otherwise.
        """
        query = self._apply_org_scope(
            super().get_query(),
            [organization_id],
        ).where(
            ProfessionalQualification.council_number == council_number,
            ProfessionalQualification.council_state == council_state,
        )
        if exclude_id:
            query = query.where(ProfessionalQualification.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def council_exists_in_family(
        self,
        council_number: str,
        council_state: str,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Check if a council registration already exists in the organization family.

        Args:
            council_number: The council registration number.
            council_state: The council state (2 chars).
            family_org_ids: List of all organization IDs in the family.
            exclude_id: Optional ID to exclude (for updates).

        Returns:
            True if council exists in the family, False otherwise.
        """
        query = self.get_query().where(
            ProfessionalQualification.organization_id.in_(list(family_org_ids)),
            ProfessionalQualification.council_number == council_number,
            ProfessionalQualification.council_state == council_state,
        )
        if exclude_id:
            query = query.where(ProfessionalQualification.id != exclude_id)

        result = await self.session.execute(select(query.exists()))
        return result.scalar_one()

    async def get_by_council(
        self,
        council_number: str,
        council_state: str,
        organization_id: UUID,
    ) -> ProfessionalQualification | None:
        """
        Get qualification by council registration.

        Args:
            council_number: The council registration number.
            council_state: The council state (2 chars).
            organization_id: The organization UUID.

        Returns:
            Qualification if found, None otherwise.
        """
        base_query = self._apply_org_scope(
            super().get_query(),
            [organization_id],
        )
        result = await self.session.execute(
            base_query.where(
                ProfessionalQualification.council_number == council_number,
                ProfessionalQualification.council_state == council_state,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_council_type(
        self,
        organization_id: UUID,
        council_type: CouncilType,
        pagination: PaginationParams,
        *,
        filters: ProfessionalQualificationFilter | None = None,
        sorting: ProfessionalQualificationSorting | None = None,
    ) -> PaginatedResponse[ProfessionalQualification]:
        """
        List qualifications by council type for an organization.

        Args:
            organization_id: The organization UUID.
            council_type: The council type (CRM, COREN, etc.).
            pagination: Pagination parameters.
            filters: Optional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of qualifications.
        """
        query = self._apply_org_scope(
            super().get_query(),
            [organization_id],
        ).where(ProfessionalQualification.council_type == council_type)
        return await self.list(
            filters=filters,
            sorting=sorting,
            limit=pagination.page_size,
            offset=(pagination.page - 1) * pagination.page_size,
            base_query=query,
        )
