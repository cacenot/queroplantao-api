"""Screening alert use case dependency injection."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.screening.use_cases import (
    CreateScreeningAlertUseCase,
    ListScreeningAlertsUseCase,
    RejectScreeningAlertUseCase,
    ResolveScreeningAlertUseCase,
)


# Alert use case factories
def get_create_screening_alert_use_case(
    session: SessionDep,
) -> CreateScreeningAlertUseCase:
    return CreateScreeningAlertUseCase(session)


def get_list_screening_alerts_use_case(
    session: SessionDep,
) -> ListScreeningAlertsUseCase:
    return ListScreeningAlertsUseCase(session)


def get_resolve_screening_alert_use_case(
    session: SessionDep,
) -> ResolveScreeningAlertUseCase:
    return ResolveScreeningAlertUseCase(session)


def get_reject_screening_alert_use_case(
    session: SessionDep,
) -> RejectScreeningAlertUseCase:
    return RejectScreeningAlertUseCase(session)


# Type aliases for dependency injection
CreateScreeningAlertUC = Annotated[
    CreateScreeningAlertUseCase, Depends(get_create_screening_alert_use_case)
]
ListScreeningAlertsUC = Annotated[
    ListScreeningAlertsUseCase, Depends(get_list_screening_alerts_use_case)
]
ResolveScreeningAlertUC = Annotated[
    ResolveScreeningAlertUseCase, Depends(get_resolve_screening_alert_use_case)
]
RejectScreeningAlertUC = Annotated[
    RejectScreeningAlertUseCase, Depends(get_reject_screening_alert_use_case)
]
