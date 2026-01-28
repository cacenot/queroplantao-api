"""Screening use case dependency injection."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.screening.use_cases import (
    ApproveDocumentUseCase,
    CancelScreeningProcessUseCase,
    CreateScreeningProcessUseCase,
    GetScreeningProcessByTokenUseCase,
    GetScreeningProcessUseCase,
    KeepExistingDocumentUseCase,
    ListMyScreeningProcessesUseCase,
    ListScreeningProcessesUseCase,
    RejectDocumentUseCase,
    RemoveRequiredDocumentUseCase,
    ReviewDocumentUseCase,
    SelectDocumentsUseCase,
    SkipClientValidationUseCase,
    UploadScreeningDocumentUseCase,
)


# Process use case factories
def get_create_screening_process_use_case(
    session: SessionDep,
) -> CreateScreeningProcessUseCase:
    return CreateScreeningProcessUseCase(session)


def get_get_screening_process_use_case(
    session: SessionDep,
) -> GetScreeningProcessUseCase:
    return GetScreeningProcessUseCase(session)


def get_get_screening_process_by_token_use_case(
    session: SessionDep,
) -> GetScreeningProcessByTokenUseCase:
    return GetScreeningProcessByTokenUseCase(session)


def get_list_screening_processes_use_case(
    session: SessionDep,
) -> ListScreeningProcessesUseCase:
    return ListScreeningProcessesUseCase(session)


def get_list_my_screening_processes_use_case(
    session: SessionDep,
) -> ListMyScreeningProcessesUseCase:
    return ListMyScreeningProcessesUseCase(session)


def get_cancel_screening_process_use_case(
    session: SessionDep,
) -> CancelScreeningProcessUseCase:
    return CancelScreeningProcessUseCase(session)


# Document use case factories
def get_select_documents_use_case(session: SessionDep) -> SelectDocumentsUseCase:
    return SelectDocumentsUseCase(session)


def get_remove_required_document_use_case(
    session: SessionDep,
) -> RemoveRequiredDocumentUseCase:
    return RemoveRequiredDocumentUseCase(session)


def get_upload_screening_document_use_case(
    session: SessionDep,
) -> UploadScreeningDocumentUseCase:
    return UploadScreeningDocumentUseCase(session)


def get_keep_existing_document_use_case(
    session: SessionDep,
) -> KeepExistingDocumentUseCase:
    return KeepExistingDocumentUseCase(session)


def get_review_document_use_case(session: SessionDep) -> ReviewDocumentUseCase:
    return ReviewDocumentUseCase(session)


def get_approve_document_use_case(session: SessionDep) -> ApproveDocumentUseCase:
    return ApproveDocumentUseCase(session)


def get_reject_document_use_case(session: SessionDep) -> RejectDocumentUseCase:
    return RejectDocumentUseCase(session)


# Validation use case factories
def get_skip_client_validation_use_case(
    session: SessionDep,
) -> SkipClientValidationUseCase:
    return SkipClientValidationUseCase(session)


# Type aliases for dependency injection
CreateScreeningProcessUC = Annotated[
    CreateScreeningProcessUseCase, Depends(get_create_screening_process_use_case)
]
GetScreeningProcessUC = Annotated[
    GetScreeningProcessUseCase, Depends(get_get_screening_process_use_case)
]
GetScreeningProcessByTokenUC = Annotated[
    GetScreeningProcessByTokenUseCase,
    Depends(get_get_screening_process_by_token_use_case),
]
ListScreeningProcessesUC = Annotated[
    ListScreeningProcessesUseCase, Depends(get_list_screening_processes_use_case)
]
ListMyScreeningProcessesUC = Annotated[
    ListMyScreeningProcessesUseCase, Depends(get_list_my_screening_processes_use_case)
]
CancelScreeningProcessUC = Annotated[
    CancelScreeningProcessUseCase, Depends(get_cancel_screening_process_use_case)
]
SelectDocumentsUC = Annotated[
    SelectDocumentsUseCase, Depends(get_select_documents_use_case)
]
RemoveRequiredDocumentUC = Annotated[
    RemoveRequiredDocumentUseCase, Depends(get_remove_required_document_use_case)
]
UploadScreeningDocumentUC = Annotated[
    UploadScreeningDocumentUseCase, Depends(get_upload_screening_document_use_case)
]
KeepExistingDocumentUC = Annotated[
    KeepExistingDocumentUseCase, Depends(get_keep_existing_document_use_case)
]
ReviewDocumentUC = Annotated[
    ReviewDocumentUseCase, Depends(get_review_document_use_case)
]
ApproveDocumentUC = Annotated[
    ApproveDocumentUseCase, Depends(get_approve_document_use_case)
]
RejectDocumentUC = Annotated[
    RejectDocumentUseCase, Depends(get_reject_document_use_case)
]
SkipClientValidationUC = Annotated[
    SkipClientValidationUseCase, Depends(get_skip_client_validation_use_case)
]
