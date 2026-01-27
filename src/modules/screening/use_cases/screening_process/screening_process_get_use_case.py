"""
Get screening process use case.

Retrieves a single screening process with all related data.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.schemas import ScreeningProcessDetailResponse
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository


class GetScreeningProcessUseCase:
    """Get a screening process by ID with all details."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
    ) -> ScreeningProcessDetailResponse:
        """
        Get screening process by ID with all related data.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.

        Returns:
            The screening process response with steps and documents.

        Raises:
            NotFoundError: If screening not found.
        """
        process = await self.repository.get_by_id_with_details(
            id=screening_id,
            organization_id=organization_id,
        )

        if not process:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(resource="Triagem", identifier=str(screening_id))

        return ScreeningProcessDetailResponse.model_validate(process)


class GetScreeningProcessByTokenUseCase:
    """Get a screening process by public access token."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)

    async def execute(
        self,
        token: str,
    ) -> ScreeningProcessDetailResponse:
        """
        Get screening process by access token with all related data.

        Args:
            token: The public access token.

        Returns:
            The screening process response with steps and documents.

        Raises:
            NotFoundError: If screening not found.
            TokenExpiredError: If token has expired.
        """
        process = await self.repository.get_by_access_token_with_details(token)

        if not process:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(resource="Triagem", identifier="token")

        return ScreeningProcessDetailResponse.model_validate(process)
