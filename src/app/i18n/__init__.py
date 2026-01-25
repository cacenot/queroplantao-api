"""Internationalization (i18n) support for error messages.

This module provides centralized message management with support for
multiple locales. Currently supports Brazilian Portuguese (pt-BR) with
the infrastructure to add English (en) and Spanish (es) in the future.

Usage:
    from src.app.i18n import get_message
    from src.app.i18n.messages import AuthMessages

    # Simple message
    msg = get_message(AuthMessages.MISSING_TOKEN)

    # Message with interpolation
    msg = get_message(
        ValidationMessages.CPF_INVALID_LENGTH,
        length=10
    )

    # Translate resource name
    name = translate_resource("OrganizationProfessional")  # → "Profissional"
"""

from typing import Any

from src.app.i18n.locales import PT_BR_MESSAGES, PT_BR_RESOURCE_NAMES
from src.app.i18n.messages import (
    AuthMessages,
    OrganizationMessages,
    ProfessionalMessages,
    ResourceMessages,
    UserMessages,
    ValidationMessages,
)

# Default locale - fixed to pt-BR for now
DEFAULT_LOCALE = "pt_br"

# Available locales and their message dictionaries
_LOCALES: dict[str, dict[str, str]] = {
    "pt_br": PT_BR_MESSAGES,
    # Future: "en": EN_MESSAGES,
    # Future: "es": ES_MESSAGES,
}

# Available locales and their resource name dictionaries
_RESOURCE_NAMES: dict[str, dict[str, str]] = {
    "pt_br": PT_BR_RESOURCE_NAMES,
    # Future: "en": EN_RESOURCE_NAMES,
    # Future: "es": ES_RESOURCE_NAMES,
}


def get_message(key: str, locale: str = DEFAULT_LOCALE, **kwargs: Any) -> str:
    """
    Get a localized message by key.

    Args:
        key: The message key (from Messages enums)
        locale: The locale to use (default: pt_br)
        **kwargs: Variables for string interpolation

    Returns:
        The translated message with any variables interpolated

    Example:
        >>> get_message(AuthMessages.MISSING_TOKEN)
        "Token de autorização é obrigatório"

        >>> get_message(ValidationMessages.CPF_INVALID_LENGTH, length=10)
        "CPF deve ter 11 dígitos, encontrado 10"
    """
    messages = _LOCALES.get(locale, _LOCALES[DEFAULT_LOCALE])
    message = messages.get(key, key)  # Fallback to key if not found

    if kwargs:
        try:
            return message.format(**kwargs)
        except KeyError:
            # If interpolation fails, return the template
            return message

    return message


def translate_resource(resource: str, locale: str = DEFAULT_LOCALE) -> str:
    """
    Translate a resource name to the specified locale.

    Args:
        resource: The resource name in English (e.g., "OrganizationProfessional")
        locale: The locale to use (default: pt_br)

    Returns:
        The translated resource name, or the original if not found

    Example:
        >>> translate_resource("OrganizationProfessional")
        "Profissional"

        >>> translate_resource("ProfessionalQualification")
        "Qualificação"
    """
    resource_names = _RESOURCE_NAMES.get(locale, _RESOURCE_NAMES[DEFAULT_LOCALE])
    return resource_names.get(resource, resource)


__all__ = [
    # Main functions
    "get_message",
    "translate_resource",
    "DEFAULT_LOCALE",
    # Message keys
    "AuthMessages",
    "OrganizationMessages",
    "ProfessionalMessages",
    "ResourceMessages",
    "UserMessages",
    "ValidationMessages",
]
