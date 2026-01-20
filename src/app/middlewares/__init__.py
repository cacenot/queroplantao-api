"""Application middlewares - Authentication, logging, error handling."""

from src.app.middlewares.constants import (
    CHILD_ORGANIZATION_ID_HEADER,
    DEFAULT_EXCLUDE_PATHS,
    ORGANIZATION_ID_HEADER,
)
from src.app.middlewares.firebase_auth import FirebaseAuthMiddleware
from src.app.middlewares.logging import LoggingMiddleware
from src.app.middlewares.organization_identity import OrganizationIdentityMiddleware

__all__ = [
    # Constants
    "DEFAULT_EXCLUDE_PATHS",
    "ORGANIZATION_ID_HEADER",
    "CHILD_ORGANIZATION_ID_HEADER",
    # Middlewares
    "LoggingMiddleware",
    "FirebaseAuthMiddleware",
    "OrganizationIdentityMiddleware",
]
