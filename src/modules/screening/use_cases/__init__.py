"""Screening module use cases."""

# Screening Alert use cases
from src.modules.screening.use_cases.screening_alert import (
    CreateScreeningAlertUseCase,
    ListScreeningAlertsUseCase,
    RejectScreeningAlertUseCase,
    ResolveScreeningAlertUseCase,
)

# Screening Process use cases
from src.modules.screening.use_cases.screening_process import (
    CancelScreeningProcessUseCase,
    CreateScreeningProcessUseCase,
    DeleteScreeningProcessUseCase,
    FinalizeScreeningProcessUseCase,
    GetScreeningProcessByTokenUseCase,
    GetScreeningProcessUseCase,
    ListScreeningProcessesUseCase,
)

# Screening Step use cases
# NOTE: CompleteClientValidationStepUseCase is commented out (broken - needs reimplementation)
from src.modules.screening.use_cases.screening_step import (
    # CompleteClientValidationStepUseCase,  # BROKEN
    CompleteConversationStepUseCase,
    CompleteDocumentReviewStepUseCase,
    CompleteDocumentUploadStepUseCase,
    CompleteSimpleStepUseCase,
    ConfigureDocumentsUseCase,
    GoBackToStepUseCase,
    ReuseDocumentUseCase,
    ReviewDocumentUseCase,
    UploadDocumentUseCase,
)

# =============================================================================
# COMMENTED OUT - Module does not exist yet
# These use cases were planned but never implemented:
# - ApproveDocumentUseCase
# - KeepExistingDocumentUseCase
# - RejectDocumentUseCase
# - RemoveRequiredDocumentUseCase
# - SelectDocumentsUseCase
# - UploadScreeningDocumentUseCase
# - SkipClientValidationUseCase
# =============================================================================

__all__ = [
    # Alerts
    "CreateScreeningAlertUseCase",
    "ListScreeningAlertsUseCase",
    "RejectScreeningAlertUseCase",
    "ResolveScreeningAlertUseCase",
    # Process
    "CancelScreeningProcessUseCase",
    "CreateScreeningProcessUseCase",
    "DeleteScreeningProcessUseCase",
    "FinalizeScreeningProcessUseCase",
    "GetScreeningProcessByTokenUseCase",
    "GetScreeningProcessUseCase",
    "ListScreeningProcessesUseCase",
    # Steps (specific use cases)
    # "CompleteClientValidationStepUseCase",  # BROKEN
    "CompleteConversationStepUseCase",
    "CompleteDocumentReviewStepUseCase",
    "CompleteDocumentUploadStepUseCase",
    "CompleteSimpleStepUseCase",
    "ConfigureDocumentsUseCase",
    "GoBackToStepUseCase",
    "ReuseDocumentUseCase",
    "ReviewDocumentUseCase",
    "UploadDocumentUseCase",
]
