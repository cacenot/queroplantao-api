"""Use case for completing document review step."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningDocumentsPendingReviewError,
    ScreeningProcessHasRejectedDocumentsError,
    ScreeningStepInvalidTypeError,
)
from src.modules.screening.domain.models.enums import (
    RequiredDocumentStatus,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.models.screening_process_step import (
    ScreeningProcessStep,
)
from src.modules.screening.domain.schemas.screening_step_complete import (
    DocumentReviewStepCompleteRequest,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningProcessStepRepository,
    ScreeningRequiredDocumentRepository,
)
from src.modules.screening.use_cases.screening_step.base_step_complete_use_case import (
    BaseStepCompleteUseCase,
)


class CompleteDocumentReviewStepUseCase(
    BaseStepCompleteUseCase[DocumentReviewStepCompleteRequest]
):
    """
    Complete the document review step.

    Validates that all documents have been reviewed (no documents with status = UPLOADED).
    If there are rejected documents, the step will return the process to DOCUMENT_UPLOAD.
    """

    step_type = StepType.DOCUMENT_REVIEW

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.required_document_repository = ScreeningRequiredDocumentRepository(session)

    async def _apply_step_data(
        self,
        step: ScreeningProcessStep,
        data: DocumentReviewStepCompleteRequest,
        completed_by: UUID,
    ) -> None:
        """Apply document review step data."""
        # Validate step type
        if step.step_type != StepType.DOCUMENT_REVIEW:
            raise ScreeningStepInvalidTypeError(
                expected=StepType.DOCUMENT_REVIEW.value,
                received=step.step_type.value,
            )

        # Get documents pending review (status = UPLOADED)
        pending_review = await self.required_document_repository.list_pending_review(
            process_id=step.process_id,
        )

        # Validate all documents have been reviewed
        if pending_review:
            pending_names = []
            for doc in pending_review:
                if doc.document_type_config:
                    pending_names.append(doc.document_type_config.name)
                elif doc.document_type:
                    pending_names.append(doc.document_type.value)
                else:
                    pending_names.append(str(doc.id))
            raise ScreeningDocumentsPendingReviewError(document_names=pending_names)

        # Check for rejected documents
        rejected_docs = await self.required_document_repository.list_rejected(
            process_id=step.process_id,
        )

        # Save review summary
        all_docs = await self.required_document_repository.list_by_process(
            process_id=step.process_id,
        )
        approved_count = sum(
            1 for doc in all_docs if doc.status == RequiredDocumentStatus.APPROVED
        )
        rejected_count = len(rejected_docs)

        step.data_references = step.data_references or {}
        step.data_references["approved_count"] = approved_count
        step.data_references["rejected_count"] = rejected_count
        step.data_references["total_documents"] = len(all_docs)

        if data.notes:
            step.review_notes = data.notes

        # If there are rejected documents, we need to return to upload step
        if rejected_docs:
            # Mark rejected documents as CORRECTION_NEEDED
            for doc in rejected_docs:
                doc.status = RequiredDocumentStatus.CORRECTION_NEEDED

            # Find the DOCUMENT_UPLOAD step and mark it as CORRECTION_NEEDED
            upload_step = await self._find_upload_step(step.process_id)
            if upload_step:
                upload_step.status = StepStatus.CORRECTION_NEEDED

            # Set step status to indicate correction is needed
            step.status = StepStatus.CORRECTION_NEEDED

            # Raise error to indicate the process needs correction
            rejected_names = []
            for doc in rejected_docs:
                if doc.document_type_config:
                    rejected_names.append(doc.document_type_config.name)
                elif doc.document_type:
                    rejected_names.append(doc.document_type.value)
                else:
                    rejected_names.append(str(doc.id))

            raise ScreeningProcessHasRejectedDocumentsError(
                document_names=rejected_names
            )

    async def _find_upload_step(
        self,
        process_id: UUID,
    ) -> ScreeningProcessStep | None:
        """Find the DOCUMENT_UPLOAD step for this process."""
        step_repo = ScreeningProcessStepRepository(self.session)
        steps = await step_repo.list_by_process(process_id)
        for s in steps:
            if s.step_type == StepType.DOCUMENT_UPLOAD:
                return s
        return None
