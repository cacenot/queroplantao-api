"""Use case for applying a pending professional version."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    VersionAlreadyAppliedError,
    VersionAlreadyRejectedError,
    VersionNotFoundError,
)
from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalVersionRepository,
)
from src.modules.professionals.use_cases.professional_version.services import (
    SnapshotApplierService,
)


class ApplyProfessionalVersionUseCase:
    """
    Use case for applying a pending professional version.

    Takes a pending version and applies its snapshot to the actual
    professional entities. Updates version status to applied.

    Note: Validation was already done at version creation time,
    so we don't re-validate here.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.version_repository = ProfessionalVersionRepository(session)
        self.snapshot_applier = SnapshotApplierService(session)

    async def execute(
        self,
        organization_id: UUID,
        version_id: UUID,
        applied_by: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
        *,
        skip_status_check: bool = False,
    ) -> OrganizationProfessional:
        """
        Apply a pending version to the professional.

        Args:
            organization_id: The organization UUID.
            version_id: The version UUID to apply.
            applied_by: UUID of the user applying the version.
            family_org_ids: Family org IDs for scope.
            skip_status_check: Skip pending status check (used internally).

        Returns:
            The updated OrganizationProfessional.

        Raises:
            VersionNotFoundError: If version doesn't exist.
            VersionAlreadyAppliedError: If version was already applied.
            VersionAlreadyRejectedError: If version was rejected.
        """
        # 1. Get version
        version = await self.version_repository.get_by_id_for_organization(
            version_id=version_id,
            organization_id=organization_id,
        )

        if version is None:
            raise VersionNotFoundError()

        # 2. Validate version is pending (unless skipped)
        if not skip_status_check:
            if version.is_applied:
                raise VersionAlreadyAppliedError()
            if version.is_rejected:
                raise VersionAlreadyRejectedError()

        # 3. Apply the snapshot
        professional = await self.snapshot_applier.apply_snapshot(
            professional_id=version.professional_id,  # type: ignore
            organization_id=organization_id,
            snapshot=version.data_snapshot,  # type: ignore
            applied_by=applied_by,
            family_org_ids=family_org_ids,
        )

        # 4. Mark previous versions as not current
        if version.professional_id:
            await self.version_repository.mark_previous_as_not_current(
                professional_id=version.professional_id,
                exclude_version_id=version_id,
            )

        # 5. Update version status
        version.is_current = True
        if not version.applied_at:
            version.applied_at = datetime.now(timezone.utc)
            version.applied_by = applied_by

        await self.session.flush()

        return professional
