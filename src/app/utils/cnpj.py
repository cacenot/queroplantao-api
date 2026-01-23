"""CNPJ validation and normalization utilities."""

import re

from src.app.i18n import ValidationMessages, get_message


def normalize_cnpj(cnpj: str) -> str:
    """
    Remove all non-digit characters from CNPJ.

    Args:
        cnpj: CNPJ string with or without formatting

    Returns:
        CNPJ with digits only

    Example:
        >>> normalize_cnpj("12.345.678/0001-90")
        "12345678000190"
    """
    return re.sub(r"\D", "", cnpj)


def validate_cnpj(cnpj: str) -> str:
    """
    Validate and normalize a Brazilian CNPJ number.

    Args:
        cnpj: CNPJ string with or without formatting (e.g., "12.345.678/0001-90")

    Returns:
        Normalized CNPJ with digits only (14 digits)

    Raises:
        ValueError: If CNPJ is invalid

    Example:
        >>> validate_cnpj("12.345.678/0001-90")
        "12345678000190"
    """
    # Remove formatting
    cnpj_digits = normalize_cnpj(cnpj)

    # Check if has 14 digits
    if len(cnpj_digits) != 14:
        raise ValueError(
            get_message(ValidationMessages.CNPJ_INVALID_LENGTH, length=len(cnpj_digits))
        )

    # Check if all digits are the same (invalid CNPJs like 11.111.111/1111-11)
    if cnpj_digits == cnpj_digits[0] * 14:
        raise ValueError(get_message(ValidationMessages.CNPJ_ALL_SAME_DIGITS))

    # Validate check digits
    def calculate_digit(cnpj_partial: str, weights: list[int]) -> int:
        """Calculate CNPJ verification digit."""
        total = sum(int(digit) * weight for digit, weight in zip(cnpj_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    # First verification digit
    first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    first_digit = calculate_digit(cnpj_digits[:12], first_weights)
    if int(cnpj_digits[12]) != first_digit:
        raise ValueError(get_message(ValidationMessages.CNPJ_INVALID_CHECK_DIGIT))

    # Second verification digit
    second_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    second_digit = calculate_digit(cnpj_digits[:13], second_weights)
    if int(cnpj_digits[13]) != second_digit:
        raise ValueError(get_message(ValidationMessages.CNPJ_INVALID_CHECK_DIGIT))

    return cnpj_digits
