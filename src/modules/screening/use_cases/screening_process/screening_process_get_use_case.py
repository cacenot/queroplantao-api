"""
Get screening process use case.

Retrieves a single screening process with all related data.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ScreeningProcessNotFoundError
from src.modules.professionals.domain.schemas import SpecialtySummary
from src.modules.screening.domain.schemas import ScreeningProcessDetailResponse
from src.modules.screening.domain.schemas.screening_process import (
    OrganizationProfessionalSummary,
)
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository
from src.modules.users.domain.schemas.organization_user import UserInfo
from src.modules.users.infrastructure.repositories import UserRepository
from src.shared.infrastructure.repositories.specialty_repository import (
    SpecialtyRepository,
)


class GetScreeningProcessUseCase:
    """Get a screening process by ID with all details."""

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
        screening_id: UUID,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
    ) -> ScreeningProcessDetailResponse:
        """
        Get screening process by ID with all related data.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            family_org_ids: Organization family IDs for scope validation.

        Returns:
            The screening process response with steps summary.

        Raises:
            ScreeningProcessNotFoundError: If screening not found.
        """
        process = await self.repository.get_by_id_with_details(
            id=screening_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        professional_summary: OrganizationProfessionalSummary | None = None
        if process.organization_professional:
            professional_summary = OrganizationProfessionalSummary.model_validate(
                process.organization_professional
            )

        response = ScreeningProcessDetailResponse.model_validate(process)
        response = response.model_copy(update={"step_info": process.step_info})
        return response.model_copy(
            update={
                "professional": professional_summary,
                "expected_specialty": await self._get_specialty_summary(
                    process.expected_specialty_id
                ),
                "owner": await self._get_user_summary(process.owner_id),
                "current_actor": await self._get_user_summary(process.current_actor_id),
                "supervisor": await self._get_user_summary(process.supervisor_id),
            }
        )


class GetScreeningProcessByTokenUseCase:
    """Get a screening process by public access token."""

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
        token: str,
    ) -> ScreeningProcessDetailResponse:
        """
        Get screening process by access token with all related data.

        Args:
            token: The public access token.

        Returns:
            The screening process response with steps summary.

        Raises:
            ScreeningProcessNotFoundError: If screening not found or token expired.
        """
        process = await self.repository.get_by_access_token_with_details(token)

        if not process:
            raise ScreeningProcessNotFoundError(screening_id="token")

        professional_summary: OrganizationProfessionalSummary | None = None
        if process.organization_professional:
            professional_summary = OrganizationProfessionalSummary.model_validate(
                process.organization_professional
            )

        response = ScreeningProcessDetailResponse.model_validate(process)
        response = response.model_copy(update={"step_info": process.step_info})
        return response.model_copy(
            update={
                "professional": professional_summary,
                "expected_specialty": await self._get_specialty_summary(
                    process.expected_specialty_id
                ),
                "owner": await self._get_user_summary(process.owner_id),
                "current_actor": await self._get_user_summary(process.current_actor_id),
                "supervisor": await self._get_user_summary(process.supervisor_id),
            }
        )
