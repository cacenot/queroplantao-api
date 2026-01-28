"""Use case for getting a professional version by ID."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import VersionNotFoundError
from src.modules.professionals.domain.models.professional_version import (
    ProfessionalVersion,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalVersionRepository,
)


class GetProfessionalVersionUseCase:
    """Use case for retrieving a single professional version."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.version_repository = ProfessionalVersionRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        version_id: UUID,
        *,
        include_diffs: bool = False,
    ) -> ProfessionalVersion:
        """
        Get a professional version by ID.

        Args:
            organization_id: The organization UUID.
            version_id: The version UUID.
            include_diffs: Whether to include diffs in response.

        Returns:
            The ProfessionalVersion.

        Raises:
            VersionNotFoundError: If version doesn't exist.
        """
        version = await self.version_repository.get_by_id_for_organization(
            version_id=version_id,
            organization_id=organization_id,
            include_diffs=include_diffs,
        )

        if version is None:
            raise VersionNotFoundError()

        return version
