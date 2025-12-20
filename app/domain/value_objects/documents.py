"""Brazilian document value objects with validation."""

from typing import Any

from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema

from app.core.utils.cnpj import normalize_cnpj, validate_cnpj
from app.core.utils.cpf import normalize_cpf, validate_cpf


class CPF(str):
    """
    CPF (Cadastro de Pessoas Físicas) string type with validation.

    Automatically validates and normalizes CPF numbers.
    Stores digits only (no formatting) in the database.

    Example:
        CPF("123.456.789-09") → "12345678909"
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Define Pydantic schema for CPF validation."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, value: str) -> "CPF":
        """Validate and normalize CPF."""
        if not isinstance(value, str):
            raise ValueError("CPF must be a string")
        normalized = validate_cpf(value)  # Raises ValueError if invalid
        return cls(normalized)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """JSON schema for OpenAPI documentation."""
        json_schema = handler(schema)
        json_schema.update(
            {
                "type": "string",
                "pattern": "^[0-9]{11}$",
                "example": "12345678909",
                "description": "Brazilian CPF number (11 digits, no formatting)",
            }
        )
        return json_schema


class CNPJ(str):
    """
    CNPJ (Cadastro Nacional da Pessoa Jurídica) string type with validation.

    Automatically validates and normalizes CNPJ numbers.
    Stores digits only (no formatting) in the database.

    Example:
        CNPJ("12.345.678/0001-90") → "12345678000190"
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Define Pydantic schema for CNPJ validation."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, value: str) -> "CNPJ":
        """Validate and normalize CNPJ."""
        if not isinstance(value, str):
            raise ValueError("CNPJ must be a string")
        normalized = validate_cnpj(value)  # Raises ValueError if invalid
        return cls(normalized)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """JSON schema for OpenAPI documentation."""
        json_schema = handler(schema)
        json_schema.update(
            {
                "type": "string",
                "pattern": "^[0-9]{14}$",
                "example": "12345678000190",
                "description": "Brazilian CNPJ number (14 digits, no formatting)",
            }
        )
        return json_schema


class CPFOrCNPJ(str):
    """
    CPF or CNPJ string type with automatic detection and validation.

    Automatically detects whether the input is a CPF (11 digits) or CNPJ (14 digits),
    validates accordingly, and normalizes to digits only.

    Example:
        CPFOrCNPJ("123.456.789-09") → "12345678909" (CPF)
        CPFOrCNPJ("12.345.678/0001-90") → "12345678000190" (CNPJ)
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Define Pydantic schema for CPF/CNPJ validation."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, value: str) -> "CPFOrCNPJ":
        """Validate and normalize CPF or CNPJ based on length."""
        if not isinstance(value, str):
            raise ValueError("CPF/CNPJ must be a string")

        # Try to normalize to see the digit count
        digits = (
            normalize_cpf(value)
            if len(normalize_cpf(value)) == 11
            else normalize_cnpj(value)
        )

        if len(digits) == 11:
            # CPF validation
            normalized = validate_cpf(value)
        elif len(digits) == 14:
            # CNPJ validation
            normalized = validate_cnpj(value)
        else:
            raise ValueError(
                "Document must be a valid CPF (11 digits) or CNPJ (14 digits)"
            )

        return cls(normalized)

    @property
    def digits_only(self) -> str:
        """
        Return the document number with digits only (no formatting).

        Note: CPFOrCNPJ is already normalized to digits only during validation,
        so this property returns the value as-is. Provided for explicit usage
        when sending to external APIs like PlugBoleto.

        Returns:
            Document number with digits only (11 for CPF, 14 for CNPJ)
        """
        return str(self)

    @property
    def is_cpf(self) -> bool:
        """Check if document is a CPF (11 digits)."""
        return len(self) == 11

    @property
    def is_cnpj(self) -> bool:
        """Check if document is a CNPJ (14 digits)."""
        return len(self) == 14

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """JSON schema for OpenAPI documentation."""
        json_schema = handler(schema)
        json_schema.update(
            {
                "type": "string",
                "pattern": "^[0-9]{11}([0-9]{3})?$",
                "example": "12345678909 or 12345678000190",
                "description": "Brazilian CPF (11 digits) or CNPJ (14 digits), no formatting",
            }
        )
        return json_schema
