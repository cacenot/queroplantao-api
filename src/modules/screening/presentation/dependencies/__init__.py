"""Screening dependencies."""

from src.modules.screening.presentation.dependencies.screening import (
    ApproveDocumentUC,
    ApproveScreeningProcessUC,
    CancelScreeningProcessUC,
    CreateScreeningProcessUC,
    GetScreeningProcessByTokenUC,
    GetScreeningProcessUC,
    KeepExistingDocumentUC,
    ListMyScreeningProcessesUC,
    ListScreeningProcessesUC,
    RejectDocumentUC,
    RejectScreeningProcessUC,
    RemoveRequiredDocumentUC,
    ReviewDocumentUC,
    SelectDocumentsUC,
    SkipClientValidationUC,
    UploadScreeningDocumentUC,
)
from src.modules.screening.presentation.dependencies.screening_step import (
    CompleteClientValidationStepUC,
    CompleteConversationStepUC,
    CompleteDocumentReviewStepUC,
    CompleteDocumentUploadStepUC,
    CompleteSimpleStepUC,
    GoBackToStepUC,
)

__all__ = [
    "ApproveDocumentUC",
    "ApproveScreeningProcessUC",
    "CancelScreeningProcessUC",
    "CreateScreeningProcessUC",
    "GetScreeningProcessByTokenUC",
    "GetScreeningProcessUC",
    "KeepExistingDocumentUC",
    "ListMyScreeningProcessesUC",
    "ListScreeningProcessesUC",
    "RejectDocumentUC",
    "RejectScreeningProcessUC",
    "RemoveRequiredDocumentUC",
    "ReviewDocumentUC",
    "SelectDocumentsUC",
    "SkipClientValidationUC",
    "UploadScreeningDocumentUC",
    # Step-specific dependencies
    "CompleteClientValidationStepUC",
    "CompleteConversationStepUC",
    "CompleteDocumentReviewStepUC",
    "CompleteDocumentUploadStepUC",
    "CompleteSimpleStepUC",
    "GoBackToStepUC",
]
