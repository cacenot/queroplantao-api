"""Application middlewares - Authentication, logging, error handling."""

from src.app.middlewares.firebase_auth import (
    DEFAULT_EXCLUDE_PATHS,
    FirebaseAuthMiddleware,
)

__all__ = [
    "DEFAULT_EXCLUDE_PATHS",
    "FirebaseAuthMiddleware",
]
