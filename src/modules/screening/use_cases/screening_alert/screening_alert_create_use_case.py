"""Use case for creating a screening alert."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningAlertAlreadyExistsError,
    ScreeningProcessInvalidStatusError,
    ScreeningProcessNotFoundError,
)
from src.modules.screening.domain.models import ScreeningStatus
from src.modules.screening.domain.models.screening_alert import ScreeningAlert
from src.modules.screening.domain.schemas.screening_alert import (
    ScreeningAlertCreate,
    ScreeningAlertResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningAlertRepository,
    ScreeningProcessRepository,
)


class CreateScreeningAlertUseCase:
    """
    Create a new screening alert.

    This use case:
    1. Validates the process exists and is in a valid state
    2. Checks there's no pending alert for this process
    3. Creates the alert with an initial note
    4. Updates process status to PENDING_SUPERVISOR
    5. Sets current_actor_id to supervisor_id
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repo = ScreeningProcessRepository(session)
        self.alert_repo = ScreeningAlertRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        process_id: UUID,
        data: ScreeningAlertCreate,
        triggered_by: UUID,
        triggered_by_name: str,
        triggered_by_role_name: str,
        family_org_ids: tuple[UUID, ...] | list[UUID] | None,
    ) -> ScreeningAlertResponse:
        """
        Execute the create alert use case.

        Args:
            organization_id: The organization UUID.
            process_id: The screening process UUID.
            data: The alert creation data.
            triggered_by: The user UUID who triggered the alert.
            triggered_by_name: The name of the user who triggered.
            triggered_by_role_name: The role display name (from database).
            family_org_ids: Organization family IDs for scope validation.

        Returns:
            The created alert response.

        Raises:
            ScreeningProcessNotFoundError: If process not found.
            ScreeningProcessInvalidStatusError: If process is not in valid state.
            ScreeningAlertAlreadyExistsError: If there's already a pending alert.
        """
        # 1. Get and validate process
        process = await self.process_repo.get_by_id_for_organization(
            id=process_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(process_id))

        # 2. Validate process status (only allow alerts for active processes)
        if process.status not in (ScreeningStatus.DRAFT, ScreeningStatus.IN_PROGRESS):
            raise ScreeningProcessInvalidStatusError(
                current_status=process.status.value
            )

        # 3. Check there's no pending alert
        has_pending = await self.alert_repo.has_pending_alert(process_id)
        if has_pending:
            raise ScreeningAlertAlreadyExistsError()

        # 4. Create the alert
        now = datetime.now(timezone.utc)
        alert = ScreeningAlert(
            process_id=process_id,
            reason=data.reason,
            category=data.category,
            is_resolved=False,
            created_by=triggered_by,
            updated_by=triggered_by,
        )

        # Add initial note
        alert.add_note(
            user_id=triggered_by,
            user_name=triggered_by_name,
            user_role_name=triggered_by_role_name,
            content=f"Alerta criado: {data.reason}",
        )

        alert = await self.alert_repo.create(alert)

        # 5. Update process status
        process.status = ScreeningStatus.PENDING_SUPERVISOR
        process.current_actor_id = process.supervisor_id
        process.updated_by = triggered_by
        process.updated_at = now

        await self.session.commit()
        await self.session.refresh(alert)

        return ScreeningAlertResponse.model_validate(alert)
