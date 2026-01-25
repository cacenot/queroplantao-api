"""Email infrastructure services."""

from src.shared.infrastructure.email.email_service import (
    EmailService,
    get_email_service,
)

__all__ = ["EmailService", "get_email_service"]
