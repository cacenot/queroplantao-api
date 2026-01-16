"""CPF validation and normalization utilities."""

import re


def normalize_cpf(cpf: str) -> str:
    """
    Remove all non-digit characters from CPF.

    Args:
        cpf: CPF string with or without formatting

    Returns:
        CPF with digits only

    Example:
        >>> normalize_cpf("123.456.789-09")
        "12345678909"
    """
    return re.sub(r"\D", "", cpf)


def validate_cpf(cpf: str) -> str:
    """
    Validate and normalize a Brazilian CPF number.

    Args:
        cpf: CPF string with or without formatting (e.g., "123.456.789-09")

    Returns:
        Normalized CPF with digits only (11 digits)

    Raises:
        ValueError: If CPF is invalid

    Example:
        >>> validate_cpf("123.456.789-09")
        "12345678909"
    """
    # Remove formatting
    cpf_digits = normalize_cpf(cpf)

    # Check if has 11 digits
    if len(cpf_digits) != 11:
        raise ValueError(f"CPF must have 11 digits, got {len(cpf_digits)}")

    # Check if all digits are the same (invalid CPFs like 111.111.111-11)
    if cpf_digits == cpf_digits[0] * 11:
        raise ValueError("CPF cannot have all digits the same")

    # Validate check digits
    def calculate_digit(cpf_partial: str, weight: int) -> int:
        """Calculate CPF verification digit."""
        total = sum(int(digit) * (weight - i) for i, digit in enumerate(cpf_partial))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    # First verification digit
    first_digit = calculate_digit(cpf_digits[:9], 10)
    if int(cpf_digits[9]) != first_digit:
        raise ValueError("Invalid CPF check digit")

    # Second verification digit
    second_digit = calculate_digit(cpf_digits[:10], 11)
    if int(cpf_digits[10]) != second_digit:
        raise ValueError("Invalid CPF check digit")

    return cpf_digits
