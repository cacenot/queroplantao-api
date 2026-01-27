"""
Client validation use case.

Handles skipping client validation step.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models.enums import (
    StepStatus,
    StepType,
)
from src.modules.screening.domain.schemas import (
    ScreeningProcessStepResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningProcessRepository,
    ScreeningProcessStepRepository,
)


class SkipClientValidationUseCase:
    """
    Skip the client validation step.

    Used when client validation is not required for this screening.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.step_repository = ScreeningProcessStepRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        skipped_by: UUID,
        reason: str | None = None,
    ) -> ScreeningProcessStepResponse:
        """
        Skip the client validation step.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            skipped_by: The user skipping the step.
            reason: Optional reason for skipping.

        Returns:
            Updated step response.
        """
        # Verify screening exists
        process = await self.process_repository.get_by_id_for_organization(
            organization_id=organization_id,
            entity_id=screening_id,
        )
        if not process:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(resource="Triagem", identifier=str(screening_id))

        # Find the client validation step
        steps = await self.step_repository.list_by_process(screening_id)
        validation_step = next(
            (s for s in steps if s.step_type == StepType.CLIENT_VALIDATION),
            None,
        )

        if not validation_step:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(
                resource="Etapa de validação do cliente", identifier=str(screening_id)
            )

        # Validate step can be skipped
        if not validation_step.is_required:
            validation_step.status = StepStatus.SKIPPED
            if reason:
                validation_step.client_validation_notes = reason
            validation_step.updated_by = skipped_by
        else:
            from src.app.exceptions import ValidationError

            raise ValidationError(
                message="Etapa de validação do cliente é obrigatória e não pode ser pulada"
            )

        await self.session.flush()
        await self.session.refresh(validation_step)

        return ScreeningProcessStepResponse.model_validate(validation_step)
