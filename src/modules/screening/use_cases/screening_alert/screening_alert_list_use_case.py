"""Use case for listing screening alerts."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ScreeningProcessNotFoundError
from src.modules.screening.domain.schemas.screening_alert import (
    ScreeningAlertListResponse,
    ScreeningAlertResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningAlertRepository,
    ScreeningProcessRepository,
)


class ListScreeningAlertsUseCase:
    """
    List alerts for a screening process.

    This use case retrieves all alerts for a process with counts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repo = ScreeningProcessRepository(session)
        self.alert_repo = ScreeningAlertRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        process_id: UUID,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
    ) -> ScreeningAlertListResponse:
        """
        Execute the list alerts use case.

        Args:
            organization_id: The organization UUID.
            process_id: The screening process UUID.
            family_org_ids: Organization family IDs for scope validation.

        Returns:
            List response with alerts and counts.

        Raises:
            ScreeningProcessNotFoundError: If process not found.
        """
        # Validate process exists
        process = await self.process_repo.get_by_id_for_organization(
            id=process_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(process_id))

        # Get alerts
        alerts = await self.alert_repo.list_for_process(process_id)

        # Get counts
        total_count, pending_count = await self.alert_repo.count_for_process(process_id)

        return ScreeningAlertListResponse(
            alerts=[ScreeningAlertResponse.model_validate(a) for a in alerts],
            total_count=total_count,
            pending_count=pending_count,
        )
