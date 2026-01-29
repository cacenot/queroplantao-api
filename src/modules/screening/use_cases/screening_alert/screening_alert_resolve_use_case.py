"""Use case for resolving a screening alert (no risk, process continues)."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningAlertAlreadyResolvedError,
    ScreeningAlertNotFoundError,
    ScreeningProcessNotFoundError,
)
from src.modules.screening.domain.models import ScreeningStatus
from src.modules.screening.domain.schemas.screening_alert import (
    ScreeningAlertResolve,
    ScreeningAlertResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningAlertRepository,
    ScreeningProcessRepository,
)


class ResolveScreeningAlertUseCase:
    """
    Resolve a screening alert (no risk confirmed).

    This use case:
    1. Validates the alert exists and is not already resolved
    2. Marks the alert as resolved
    3. Adds resolution note
    4. Returns process status to IN_PROGRESS
    5. Sets current_actor_id back to owner_id
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repo = ScreeningProcessRepository(session)
        self.alert_repo = ScreeningAlertRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        process_id: UUID,
        alert_id: UUID,
        data: ScreeningAlertResolve,
        resolved_by: UUID,
        resolved_by_name: str,
        resolved_by_role_name: str,
    ) -> ScreeningAlertResponse:
        """
        Execute the resolve alert use case.

        Args:
            organization_id: The organization UUID.
            process_id: The screening process UUID.
            alert_id: The alert UUID.
            data: The resolution data.
            resolved_by: The user UUID who is resolving.
            resolved_by_name: The name of the user.
            resolved_by_role_name: The role display name (from database).

        Returns:
            The updated alert response.

        Raises:
            ScreeningProcessNotFoundError: If process not found.
            ScreeningAlertNotFoundError: If alert not found.
            ScreeningAlertAlreadyResolvedError: If alert already resolved.
        """
        # 1. Validate process exists
        process = await self.process_repo.get_by_id_for_organization(
            process_id, organization_id
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(process_id))

        # 2. Get and validate alert
        alert = await self.alert_repo.get_by_id_for_process(alert_id, process_id)
        if not alert:
            raise ScreeningAlertNotFoundError(alert_id=str(alert_id))

        if alert.is_resolved:
            raise ScreeningAlertAlreadyResolvedError(alert_id=str(alert_id))

        # 3. Resolve the alert
        now = datetime.now(timezone.utc)
        alert.is_resolved = True
        alert.resolved_at = now
        alert.resolved_by = resolved_by
        alert.updated_by = resolved_by

        # Add resolution note
        alert.add_note(
            user_id=resolved_by,
            user_name=resolved_by_name,
            user_role_name=resolved_by_role_name,
            content=f"Alerta resolvido: {data.resolution_notes}",
        )

        # 4. Update process status back to IN_PROGRESS
        process.status = ScreeningStatus.IN_PROGRESS
        process.current_actor_id = process.owner_id
        process.updated_by = resolved_by
        process.updated_at = now

        await self.session.commit()
        await self.session.refresh(alert)

        return ScreeningAlertResponse.model_validate(alert)
