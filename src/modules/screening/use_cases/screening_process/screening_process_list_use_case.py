"""
List screening processes use case.

Lists screening processes with pagination and filters.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.schemas import SpecialtySummary
from src.modules.screening.domain.schemas import ScreeningProcessListResponse
from src.modules.screening.domain.schemas.screening_process import (
    OrganizationProfessionalSummary,
)
from src.modules.screening.infrastructure.filters import (
    ScreeningProcessFilter,
    ScreeningProcessSorting,
)
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository
from src.modules.users.domain.schemas.organization_user import UserInfo
from src.modules.users.infrastructure.repositories import UserRepository
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)


class ListScreeningProcessesUseCase:
    """List screening processes for an organization."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.user_repository = UserRepository(session)
        self.specialty_repository = SpecialtyRepository(session)

    async def _get_user_summary(self, user_id: UUID | None) -> UserInfo | None:
        if user_id is None:
            return None
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        return UserInfo.model_validate(user)

    async def _get_specialty_summary(
        self, specialty_id: UUID | None
    ) -> SpecialtySummary | None:
        if specialty_id is None:
            return None
        specialty = await self.specialty_repository.get_by_id(specialty_id)
        if specialty is None:
            return None
        return SpecialtySummary.model_validate(specialty)

    async def execute(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
        filters: ScreeningProcessFilter | None = None,
        sorting: ScreeningProcessSorting | None = None,
    ) -> PaginatedResponse[ScreeningProcessListResponse]:
        """
        List screening processes with pagination.

        Args:
            organization_id: The organization ID.
            pagination: Pagination parameters.
            family_org_ids: Organization family IDs for scope validation.
            filters: Optional filter parameters.
            sorting: Optional sorting parameters.

        Returns:
            Paginated list of screening processes.
        """
        result = await self.repository.list_for_organization(
            organization_id=organization_id,
            pagination=pagination,
            family_org_ids=family_org_ids,
            filters=filters,
            sorting=sorting,
        )

        # Collect all unique IDs for batch loading
        owner_ids: set[UUID] = set()
        actor_ids: set[UUID] = set()
        supervisor_ids: set[UUID] = set()
        specialty_ids: set[UUID] = set()

        for item in result.items:
            if item.owner_id:
                owner_ids.add(item.owner_id)
            if item.current_actor_id:
                actor_ids.add(item.current_actor_id)
            if item.supervisor_id:
                supervisor_ids.add(item.supervisor_id)
            if item.expected_specialty_id:
                specialty_ids.add(item.expected_specialty_id)

        # Get all unique user IDs
        all_user_ids = owner_ids | actor_ids | supervisor_ids

        # Batch load users and specialties
        users_map: dict[UUID, UserInfo] = {}
        for user_id in all_user_ids:
            user_info = await self._get_user_summary(user_id)
            if user_info:
                users_map[user_id] = user_info

        specialties_map: dict[UUID, SpecialtySummary] = {}
        for specialty_id in specialty_ids:
            specialty = await self._get_specialty_summary(specialty_id)
            if specialty:
                specialties_map[specialty_id] = specialty

        items = []
        for item in result.items:
            # Build professional summary if linked
            professional_summary: OrganizationProfessionalSummary | None = None
            if item.organization_professional:
                professional_summary = OrganizationProfessionalSummary.model_validate(
                    item.organization_professional
                )

            response = ScreeningProcessListResponse.model_validate(item)
            response = response.model_copy(
                update={
                    "step_info": item.step_info,
                    "professional": professional_summary,
                    "expected_specialty": (
                        specialties_map.get(item.expected_specialty_id)
                        if item.expected_specialty_id
                        else None
                    ),
                    "owner": (users_map.get(item.owner_id) if item.owner_id else None),
                    "current_actor": (
                        users_map.get(item.current_actor_id)
                        if item.current_actor_id
                        else None
                    ),
                    "supervisor": (
                        users_map.get(item.supervisor_id)
                        if item.supervisor_id
                        else None
                    ),
                }
            )
            items.append(response)
        return PaginatedResponse[ScreeningProcessListResponse](
            items=items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
            has_next=result.has_next,
            has_previous=result.has_previous,
        )
