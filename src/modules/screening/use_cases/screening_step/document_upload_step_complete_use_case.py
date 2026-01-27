"""Use case for completing document upload step."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ScreeningDocumentsNotUploadedError,
    ScreeningStepInvalidTypeError,
)
from src.modules.screening.domain.models.enums import RequiredDocumentStatus, StepType
from src.modules.screening.domain.models.screening_process_step import (
    ScreeningProcessStep,
)
from src.modules.screening.domain.schemas.screening_step_complete import (
    DocumentUploadStepCompleteRequest,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningRequiredDocumentRepository,
)
from src.modules.screening.use_cases.screening_step.base_step_complete_use_case import (
    BaseStepCompleteUseCase,
)


class CompleteDocumentUploadStepUseCase(
    BaseStepCompleteUseCase[DocumentUploadStepCompleteRequest]
):
    """
    Complete the document upload step.

    Validates that all required documents have been uploaded (status = UPLOADED).
    This step is completed by the professional or user after uploading all documents.
    """

    step_type = StepType.DOCUMENT_UPLOAD

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.required_document_repository = ScreeningRequiredDocumentRepository(session)

    async def _apply_step_data(
        self,
        step: ScreeningProcessStep,
        data: DocumentUploadStepCompleteRequest,
        completed_by: UUID,
    ) -> None:
        """Apply document upload step data."""
        # Validate step type
        if step.step_type != StepType.DOCUMENT_UPLOAD:
            raise ScreeningStepInvalidTypeError(
                expected=StepType.DOCUMENT_UPLOAD.value,
                received=step.step_type.value,
            )

        # Get all required documents for this process
        pending_uploads = (
            await self.required_document_repository.list_required_not_uploaded(
                process_id=step.process_id,
            )
        )

        # Validate all required documents have been uploaded
        if pending_uploads:
            # Get document names for error message
            pending_names = []
            for doc in pending_uploads:
                if doc.document_type_config:
                    pending_names.append(doc.document_type_config.name)
                elif doc.document_type:
                    pending_names.append(doc.document_type.value)
                else:
                    pending_names.append(str(doc.id))
            raise ScreeningDocumentsNotUploadedError(document_names=pending_names)

        # Get all uploaded documents for reference
        uploaded_docs = await self.required_document_repository.list_by_status(
            process_id=step.process_id,
            status=RequiredDocumentStatus.UPLOADED,
        )

        # Save document references
        step.data_references = step.data_references or {}
        step.data_references["document_ids"] = [str(doc.id) for doc in uploaded_docs]
        step.data_references["total_documents"] = len(uploaded_docs)

        if data.notes:
            step.review_notes = data.notes
