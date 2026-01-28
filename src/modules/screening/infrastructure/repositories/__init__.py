"""Screening module repositories."""

from src.modules.screening.infrastructure.repositories.organization_screening_settings_repository import (
    OrganizationScreeningSettingsRepository,
)
from src.modules.screening.infrastructure.repositories.screening_document_repository import (
    ScreeningDocumentRepository,
)
from src.modules.screening.infrastructure.repositories.screening_process_repository import (
    ScreeningProcessRepository,
)
from src.modules.screening.infrastructure.repositories.step_repositories import (
    BaseStepRepository,
    ClientValidationStepRepository,
    ConversationStepRepository,
    DocumentReviewStepRepository,
    DocumentUploadStepRepository,
    PaymentInfoStepRepository,
    ProfessionalDataStepRepository,
    SupervisorReviewStepRepository,
)

# =============================================================================
# DEPRECATED ALIASES - Remove after use_cases refactoring
# These exist only for backward compatibility with use_cases that haven't
# been updated to use the new repository structure yet.
# =============================================================================

# Old ScreeningProcessStepRepository -> now use individual step repositories
# (ConversationStepRepository, DocumentUploadStepRepository, etc.)
ScreeningProcessStepRepository = BaseStepRepository

# Old ScreeningRequiredDocumentRepository -> now ScreeningDocumentRepository
# (Documents are now unified - requirements + reviews in single model)
ScreeningRequiredDocumentRepository = ScreeningDocumentRepository

# Old ScreeningDocumentReviewRepository -> now ScreeningDocumentRepository
# (Review data is now part of ScreeningDocument model)
ScreeningDocumentReviewRepository = ScreeningDocumentRepository

# =============================================================================

__all__ = [
    # Settings
    "OrganizationScreeningSettingsRepository",
    # Process
    "ScreeningProcessRepository",
    # Document
    "ScreeningDocumentRepository",
    # Steps (base)
    "BaseStepRepository",
    # Steps (specific)
    "ConversationStepRepository",
    "ProfessionalDataStepRepository",
    "DocumentUploadStepRepository",
    "DocumentReviewStepRepository",
    "PaymentInfoStepRepository",
    "SupervisorReviewStepRepository",
    "ClientValidationStepRepository",
    # DEPRECATED - Remove after use_cases refactoring
    "ScreeningProcessStepRepository",
    "ScreeningRequiredDocumentRepository",
    "ScreeningDocumentReviewRepository",
]
