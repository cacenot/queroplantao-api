"""Screening dependencies."""

from src.modules.screening.presentation.dependencies.screening import (
    ApproveDocumentUC,
    CancelScreeningProcessUC,
    CreateScreeningProcessUC,
    GetScreeningProcessByTokenUC,
    GetScreeningProcessUC,
    KeepExistingDocumentUC,
    ListMyScreeningProcessesUC,
    ListScreeningProcessesUC,
    RejectDocumentUC,
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
    CompleteProfessionalDataStepUC,
    GoBackToStepUC,
)

__all__ = [
    "ApproveDocumentUC",
    "CancelScreeningProcessUC",
    "CreateScreeningProcessUC",
    "GetScreeningProcessByTokenUC",
    "GetScreeningProcessUC",
    "KeepExistingDocumentUC",
    "ListMyScreeningProcessesUC",
    "ListScreeningProcessesUC",
    "RejectDocumentUC",
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
    "CompleteProfessionalDataStepUC",
    "GoBackToStepUC",
]
