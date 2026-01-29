"""Finalize screening process use case."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningProcessNotFoundError,
    ValidationError,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)
from src.modules.screening.domain.models.enums import ScreeningStatus, StepStatus
from src.modules.screening.domain.schemas import ScreeningProcessResponse
from src.modules.screening.infrastructure.repositories import ScreeningProcessRepository


class FinalizeScreeningProcessUseCase:
    """
    Finalize a screening process and approve all pending documents.

    This use case:
    1. Validates all required steps are completed/approved
    2. Promotes all pending documents (is_pending=False)
    3. Updates the screening status to APPROVED
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScreeningProcessRepository(session)
        self.document_repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        finalized_by: UUID,
    ) -> ScreeningProcessResponse:
        """
        Finalize the screening process.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            finalized_by: The user finalizing the screening.

        Returns:
            The finalized screening process response.

        Raises:
            ScreeningProcessNotFoundError: If screening not found.
            ValidationError: If screening cannot be finalized.
        """
        process = await self.repository.get_by_id_with_details(
            id=screening_id,
            organization_id=organization_id,
        )
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(screening_id))

        # Validate screening is in progress
        if process.status != ScreeningStatus.IN_PROGRESS:
            raise ValidationError(
                message=f"Triagem não pode ser finalizada no status {process.status.value}. "
                "Apenas triagens em andamento podem ser finalizadas.",
            )

        # Validate all required steps are completed
        incomplete_steps = self._get_incomplete_steps(process)
        if incomplete_steps:
            raise ValidationError(
                message=f"Não é possível finalizar a triagem. "
                f"Etapas pendentes: {', '.join(incomplete_steps)}",
            )

        # Promote all pending documents
        promoted_count = await self.document_repository.promote_pending_documents(
            screening_id=screening_id,
            promoted_by=finalized_by,
        )

        # Update screening status to APPROVED
        process.status = ScreeningStatus.APPROVED
        process.completed_at = datetime.now(UTC)
        process.updated_by = finalized_by

        await self.session.flush()
        await self.session.refresh(process)

        # Log the promotion count (for debugging)
        # In production, consider adding this to the response or audit log
        _ = promoted_count

        return ScreeningProcessResponse.model_validate(process)

    def _get_incomplete_steps(self, process) -> list[str]:
        """
        Get list of incomplete required steps.

        Returns:
            List of step names that are not completed/approved.
        """
        incomplete = []

        # Check each step that should be completed
        # Only check steps that are configured (not None)
        step_checks = [
            (process.conversation_step, "Conversa Inicial"),
            (process.professional_data_step, "Dados do Profissional"),
            (process.document_upload_step, "Upload de Documentos"),
            (process.document_review_step, "Revisão de Documentos"),
            (process.payment_info_step, "Dados de Pagamento"),
            (process.client_validation_step, "Validação do Cliente"),
        ]

        completed_statuses = (
            StepStatus.COMPLETED,
            StepStatus.APPROVED,
            StepStatus.SKIPPED,
        )

        for step, name in step_checks:
            if step is not None and step.status not in completed_statuses:
                incomplete.append(name)

        return incomplete
