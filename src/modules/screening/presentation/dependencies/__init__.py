"""Screening dependencies."""

from src.modules.screening.presentation.dependencies.screening import (
    CancelScreeningProcessUC,
    CreateScreeningProcessUC,
    FinalizeScreeningProcessUC,
    GetScreeningProcessByTokenUC,
    GetScreeningProcessUC,
    ListScreeningProcessesUC,
    ReuseDocumentUC,
    ReviewDocumentUC,
)
from src.modules.screening.presentation.dependencies.screening_alert import (
    CreateScreeningAlertUC,
    ListScreeningAlertsUC,
    RejectScreeningAlertUC,
    ResolveScreeningAlertUC,
)
from src.modules.screening.presentation.dependencies.screening_document import (
    ConfigureDocumentsUC,
    ReviewDocumentUC as ReviewDocumentStepUC,
    UploadDocumentUC,
)
from src.modules.screening.presentation.dependencies.screening_step import (
    # CompleteClientValidationStepUC,  # BROKEN - commented out
    CompleteConversationStepUC,
    CompleteDocumentReviewStepUC,
    CompleteDocumentUploadStepUC,
    CompleteProfessionalDataStepUC,
    GoBackToStepUC,
)

# =============================================================================
# NOTE: The following type aliases don't exist (use cases never implemented):
# - ApproveDocumentUC
# - KeepExistingDocumentUC
# - RejectDocumentUC
# - RemoveRequiredDocumentUC
# - SelectDocumentsUC
# - SkipClientValidationUC
# - UploadScreeningDocumentUC
# =============================================================================

__all__ = [
    "CancelScreeningProcessUC",
    "CreateScreeningProcessUC",
    "FinalizeScreeningProcessUC",
    "GetScreeningProcessByTokenUC",
    "GetScreeningProcessUC",
    "ListScreeningProcessesUC",
    "ReuseDocumentUC",
    "ReviewDocumentUC",
    # Alert dependencies
    "CreateScreeningAlertUC",
    "ListScreeningAlertsUC",
    "RejectScreeningAlertUC",
    "ResolveScreeningAlertUC",
    # Step-specific dependencies
    # "CompleteClientValidationStepUC",  # BROKEN - commented out
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
