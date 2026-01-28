"""Step repositories for screening workflow."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.screening.domain.models import (
    StepStatus,
)
from src.modules.screening.domain.models.steps import (
    ClientValidationStep,
    ConversationStep,
    DocumentReviewStep,
    DocumentUploadStep,
    PaymentInfoStep,
    ProfessionalDataStep,
    ScreeningStepMixin,
    SupervisorReviewStep,
)
from src.shared.infrastructure.repositories import BaseRepository


# Type variable for step models
StepT = TypeVar("StepT", bound=ScreeningStepMixin)


class BaseStepRepository(Generic[StepT], BaseRepository[StepT]):
    """
    Base repository for screening step models.

    Provides common operations for all step types.
    Steps don't have soft delete - they're tied to the process lifecycle.
    """

    def _base_query(self) -> Select[tuple[StepT]]:
        """Get base query for the step model."""
        return select(self.model)

    async def get_by_process_id(
        self,
        process_id: UUID,
    ) -> StepT | None:
        """
        Get step by process ID.

        Each step type has a unique constraint on process_id, so there's at most one.

        Args:
            process_id: The screening process UUID.

        Returns:
            Step if found, None otherwise.
        """
        query = self._base_query().where(self.model.process_id == process_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def exists_for_process(
        self,
        process_id: UUID,
    ) -> bool:
        """
        Check if step exists for a process.

        Args:
            process_id: The screening process UUID.

        Returns:
            True if step exists, False otherwise.
        """
        query = (
            select(self.model.id).where(self.model.process_id == process_id).limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None


class ConversationStepRepository(BaseStepRepository[ConversationStep]):
    """
    Repository for ConversationStep model.

    Initial phone screening step.
    """

    model = ConversationStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)


class ProfessionalDataStepRepository(BaseStepRepository[ProfessionalDataStep]):
    """
    Repository for ProfessionalDataStep model.

    Professional data collection step with version tracking.
    """

    model = ProfessionalDataStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_process_id_with_version(
        self,
        process_id: UUID,
    ) -> ProfessionalDataStep | None:
        """
        Get step with professional version loaded.

        Args:
            process_id: The screening process UUID.

        Returns:
            Step with professional_version loaded, or None.
        """
        query = (
            self._base_query()
            .where(ProfessionalDataStep.process_id == process_id)
            .options(selectinload(ProfessionalDataStep.professional_version))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class DocumentUploadStepRepository(BaseStepRepository[DocumentUploadStep]):
    """
    Repository for DocumentUploadStep model.

    Document upload step with document list.
    """

    model = DocumentUploadStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_process_id_with_documents(
        self,
        process_id: UUID,
    ) -> DocumentUploadStep | None:
        """
        Get step with documents loaded.

        Args:
            process_id: The screening process UUID.

        Returns:
            Step with documents loaded, or None.
        """
        query = (
            self._base_query()
            .where(DocumentUploadStep.process_id == process_id)
            .options(selectinload(DocumentUploadStep.documents))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_documents(
        self,
        id: UUID,
    ) -> DocumentUploadStep | None:
        """
        Get step by ID with documents loaded.

        Args:
            id: The step UUID.

        Returns:
            Step with documents loaded, or None.
        """
        query = (
            self._base_query()
            .where(DocumentUploadStep.id == id)
            .options(selectinload(DocumentUploadStep.documents))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class DocumentReviewStepRepository(BaseStepRepository[DocumentReviewStep]):
    """
    Repository for DocumentReviewStep model.

    Document review step with reference to upload step.
    """

    model = DocumentReviewStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_process_id_with_upload_step(
        self,
        process_id: UUID,
    ) -> DocumentReviewStep | None:
        """
        Get step with upload step loaded.

        Args:
            process_id: The screening process UUID.

        Returns:
            Step with upload_step loaded, or None.
        """
        query = (
            self._base_query()
            .where(DocumentReviewStep.process_id == process_id)
            .options(selectinload(DocumentReviewStep.upload_step))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class PaymentInfoStepRepository(BaseStepRepository[PaymentInfoStep]):
    """
    Repository for PaymentInfoStep model.

    Payment information step (bank account and company).
    """

    model = PaymentInfoStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_process_id_with_relations(
        self,
        process_id: UUID,
    ) -> PaymentInfoStep | None:
        """
        Get step with company and bank account loaded.

        Args:
            process_id: The screening process UUID.

        Returns:
            Step with relations loaded, or None.
        """
        query = (
            self._base_query()
            .where(PaymentInfoStep.process_id == process_id)
            .options(
                selectinload(PaymentInfoStep.company),
                selectinload(PaymentInfoStep.bank_account),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class SupervisorReviewStepRepository(BaseStepRepository[SupervisorReviewStep]):
    """
    Repository for SupervisorReviewStep model.

    Supervisor review step for escalations.
    """

    model = SupervisorReviewStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_pending_for_supervisor(
        self,
        supervisor_id: UUID,
    ) -> list[SupervisorReviewStep]:
        """
        List pending steps assigned to a supervisor.

        Args:
            supervisor_id: The supervisor user UUID.

        Returns:
            List of pending steps assigned to the supervisor.
        """
        query = (
            self._base_query()
            .where(SupervisorReviewStep.assigned_to == supervisor_id)
            .where(
                SupervisorReviewStep.status.in_(
                    [StepStatus.PENDING, StepStatus.IN_PROGRESS]
                )
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class ClientValidationStepRepository(BaseStepRepository[ClientValidationStep]):
    """
    Repository for ClientValidationStep model.

    Client validation step for final approval.
    """

    model = ClientValidationStep

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_process_id_with_process(
        self,
        process_id: UUID,
    ) -> ClientValidationStep | None:
        """
        Get step with process loaded.

        Args:
            process_id: The screening process UUID.

        Returns:
            Step with process loaded, or None.
        """
        query = (
            self._base_query()
            .where(ClientValidationStep.process_id == process_id)
            .options(selectinload(ClientValidationStep.process))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
