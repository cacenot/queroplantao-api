"""Screening module use cases."""

# Screening Process use cases
from src.modules.screening.use_cases.screening_process import (
    CancelScreeningProcessUseCase,
    CreateScreeningProcessUseCase,
    FinalizeScreeningProcessUseCase,
    GetScreeningProcessByTokenUseCase,
    GetScreeningProcessUseCase,
    ListMyScreeningProcessesUseCase,
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
    # Process
    "CancelScreeningProcessUseCase",
    "CreateScreeningProcessUseCase",
    "FinalizeScreeningProcessUseCase",
    "GetScreeningProcessByTokenUseCase",
    "GetScreeningProcessUseCase",
    "ListMyScreeningProcessesUseCase",
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
