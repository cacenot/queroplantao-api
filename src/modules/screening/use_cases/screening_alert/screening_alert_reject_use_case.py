"""Use case for rejecting a screening via alert (risk confirmed)."""

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
    ScreeningAlertReject,
    ScreeningAlertResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningAlertRepository,
    ScreeningProcessRepository,
)


class RejectScreeningAlertUseCase:
    """
    Reject a screening via alert (risk confirmed).

    This use case:
    1. Validates the alert exists and is not already resolved
    2. Marks the alert as resolved
    3. Adds rejection note
    4. Sets process status to REJECTED
    5. Populates rejection_reason from alert + notes
    6. Sets current_actor_id to None
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
        data: ScreeningAlertReject,
        rejected_by: UUID,
        rejected_by_name: str,
        rejected_by_role_name: str,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
    ) -> ScreeningAlertResponse:
        """
        Execute the reject via alert use case.

        Args:
            organization_id: The organization UUID.
            process_id: The screening process UUID.
            alert_id: The alert UUID.
            data: The rejection data.
            rejected_by: The user UUID who is rejecting.
            rejected_by_name: The name of the user.
            rejected_by_role_name: The role display name (from database).
            family_org_ids: Organization family IDs for scope validation.

        Returns:
            The updated alert response.

        Raises:
            ScreeningProcessNotFoundError: If process not found.
            ScreeningAlertNotFoundError: If alert not found.
            ScreeningAlertAlreadyResolvedError: If alert already resolved.
        """
        # 1. Validate process exists
        process = await self.process_repo.get_by_id_for_organization(
            id=process_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(process_id))

        # 2. Get and validate alert
        alert = await self.alert_repo.get_by_id_for_process(alert_id, process_id)
        if not alert:
            raise ScreeningAlertNotFoundError(alert_id=str(alert_id))

        if alert.is_resolved:
            raise ScreeningAlertAlreadyResolvedError(alert_id=str(alert_id))

        # 3. Resolve the alert (rejection is also a resolution)
        now = datetime.now(timezone.utc)
        alert.is_resolved = True
        alert.resolved_at = now
        alert.resolved_by = rejected_by
        alert.updated_by = rejected_by

        # Add rejection note
        alert.add_note(
            user_id=rejected_by,
            user_name=rejected_by_name,
            user_role_name=rejected_by_role_name,
            content=f"Triagem rejeitada: {data.rejection_notes}",
        )

        # 4. Build rejection reason from alert data
        rejection_reason = (
            f"[Alerta - {alert.category.value}] {alert.reason}\n\n"
            f"Decisão do supervisor: {data.rejection_notes}"
        )

        # 5. Update process status to REJECTED
        process.status = ScreeningStatus.REJECTED
        process.rejection_reason = rejection_reason
        process.current_actor_id = None  # No more actions needed
        process.updated_by = rejected_by
        process.updated_at = now

        await self.session.commit()
        await self.session.refresh(alert)

        return ScreeningAlertResponse.model_validate(alert)
