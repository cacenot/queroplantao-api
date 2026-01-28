"""Screening dependencies."""

from src.modules.screening.presentation.dependencies.screening import (
    ApproveDocumentUC,
    CancelScreeningProcessUC,
    CreateScreeningProcessUC,
    FinalizeScreeningProcessUC,
    GetScreeningProcessByTokenUC,
    GetScreeningProcessUC,
    KeepExistingDocumentUC,
    ListMyScreeningProcessesUC,
    ListScreeningProcessesUC,
    RejectDocumentUC,
    RemoveRequiredDocumentUC,
    ReuseDocumentUC,
    ReviewDocumentUC,
    SelectDocumentsUC,
    SkipClientValidationUC,
    UploadScreeningDocumentUC,
)
from src.modules.screening.presentation.dependencies.screening_document import (
    ConfigureDocumentsUC,
    ReviewDocumentUC as ReviewDocumentStepUC,
    UploadDocumentUC,
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
    "FinalizeScreeningProcessUC",
    "GetScreeningProcessByTokenUC",
    "GetScreeningProcessUC",
    "KeepExistingDocumentUC",
    "ListMyScreeningProcessesUC",
    "ListScreeningProcessesUC",
    "RejectDocumentUC",
    "RemoveRequiredDocumentUC",
    "ReuseDocumentUC",
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
    # Document step dependencies
    "ConfigureDocumentsUC",
    "ReviewDocumentStepUC",
    "UploadDocumentUC",
]
