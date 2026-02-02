"""Dependencies for screening document use cases."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep, SettingsDep
from src.modules.screening.use_cases.screening_step.document_review import (
    ReviewDocumentUseCase,
)
from src.modules.screening.use_cases.screening_step.document_upload import (
    ConfigureDocumentsUseCase,
    UploadDocumentUseCase,
)


# =============================================================================
# DOCUMENT UPLOAD USE CASE FACTORIES
# =============================================================================


def get_configure_documents_use_case(
    session: SessionDep,
) -> ConfigureDocumentsUseCase:
    """Factory for ConfigureDocumentsUseCase."""
    return ConfigureDocumentsUseCase(session)


def get_upload_document_use_case(
    session: SessionDep,
    settings: SettingsDep,
) -> UploadDocumentUseCase:
    """Factory for UploadDocumentUseCase."""
    return UploadDocumentUseCase(session, settings)


# =============================================================================
# DOCUMENT REVIEW USE CASE FACTORIES
# =============================================================================


def get_review_document_use_case(
    session: SessionDep,
) -> ReviewDocumentUseCase:
    """Factory for ReviewDocumentUseCase."""
    return ReviewDocumentUseCase(session)


# =============================================================================
# TYPE ALIASES FOR ROUTE SIGNATURES
# =============================================================================

ConfigureDocumentsUC = Annotated[
    ConfigureDocumentsUseCase,
    Depends(get_configure_documents_use_case),
]

UploadDocumentUC = Annotated[
    UploadDocumentUseCase,
    Depends(get_upload_document_use_case),
]

ReviewDocumentUC = Annotated[
    ReviewDocumentUseCase,
    Depends(get_review_document_use_case),
]
