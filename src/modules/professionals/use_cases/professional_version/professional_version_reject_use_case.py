"""Use case for rejecting a pending professional version."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    VersionAlreadyAppliedError,
    VersionAlreadyRejectedError,
    VersionNotFoundError,
)
from src.modules.professionals.domain.models.professional_version import (
    ProfessionalVersion,
)
from src.modules.professionals.domain.schemas.professional_version import (
    ProfessionalVersionReject,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalVersionRepository,
)


class RejectProfessionalVersionUseCase:
    """
    Use case for rejecting a pending professional version.

    Marks a pending version as rejected with a reason.
    Rejected versions cannot be applied.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.version_repository = ProfessionalVersionRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        version_id: UUID,
        data: ProfessionalVersionReject,
        rejected_by: UUID,
    ) -> ProfessionalVersion:
        """
        Reject a pending version.

        Args:
            organization_id: The organization UUID.
            version_id: The version UUID to reject.
            data: Rejection data with reason.
            rejected_by: UUID of the user rejecting the version.

        Returns:
            The rejected ProfessionalVersion.

        Raises:
            VersionNotFoundError: If version doesn't exist.
            VersionAlreadyAppliedError: If version was already applied.
            VersionAlreadyRejectedError: If version was already rejected.
        """
        # 1. Get version
        version = await self.version_repository.get_by_id_for_organization(
            version_id=version_id,
            organization_id=organization_id,
        )

        if version is None:
            raise VersionNotFoundError()

        # 2. Validate version is pending
        if version.is_applied:
            raise VersionAlreadyAppliedError()
        if version.is_rejected:
            raise VersionAlreadyRejectedError()

        # 3. Mark as rejected
        version.rejected_at = datetime.now(timezone.utc)
        version.rejected_by = rejected_by
        version.rejection_reason = data.rejection_reason

        await self.session.flush()

        return version
