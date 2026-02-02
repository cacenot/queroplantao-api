"""Delete screening process use case."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ScreeningProcessNotFoundError
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository


class DeleteScreeningProcessUseCase:
    """Use case for soft-deleting a screening process."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        deleted_by: UUID,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
    ) -> None:
        """
        Soft delete a screening process.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            deleted_by: The user deleting the screening.
            family_org_ids: Organization family IDs for scope validation.

        Raises:
            ScreeningProcessNotFoundError: If screening not found.
        """
        process = await self.repository.get_by_id_for_organization(
            id=screening_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if process is None:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        process.deleted_at = datetime.now(UTC)
        process.updated_by = deleted_by
        await self.session.flush()
