"""Address-related value objects with validation."""

import re
from typing import Any

from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema


class PostalCode(str):
    """
    Brazilian postal code (CEP) string type with validation.

    Automatically validates and normalizes CEP numbers.
    Stores digits only (no formatting) in the database.

    Example:
        PostalCode("12345-678") → "12345678"
    """

    def __new__(cls, value: str) -> "PostalCode":
        """Validate and normalize on instantiation."""
        if isinstance(value, cls):
            return value
        return cls._validate(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Define Pydantic schema for postal code validation."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, value: str) -> "PostalCode":
        """Validate and normalize postal code (CEP)."""
        if not isinstance(value, str):
            raise ValueError("Postal code must be a string")

        # Remove all non-digit characters
        digits = re.sub(r"\D", "", value)

        # Validate length (CEP has 8 digits)
        if len(digits) != 8:
            raise ValueError(f"CEP must have 8 digits, got {len(digits)}")

        # Basic sanity check: not all zeros
        if digits == "00000000":
            raise ValueError("Invalid CEP: cannot be all zeros")

        return str.__new__(cls, digits)  # Avoid recursion

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """JSON schema for OpenAPI documentation."""
        json_schema = handler(schema)
        json_schema.update(
            {
                "type": "string",
                "pattern": "^[0-9]{8}$",
                "example": "12345678",
                "description": "Brazilian postal code (CEP) with 8 digits, no formatting",
            }
        )
        return json_schema

    @property
    def formatted(self) -> str:
        """
        Return the postal code in formatted display format.

        Returns:
            Formatted CEP (e.g., "12345-678").
        """
        if len(self) != 8:
            return str(self)
        return f"{self[:5]}-{self[5:]}"

    @property
    def region(self) -> str:
        """
        Extract the region code from the CEP (first digit).

        CEP regions in Brazil:
        - 0: São Paulo (Metropolitan)
        - 1: São Paulo (Interior)
        - 2: Rio de Janeiro and Espírito Santo
        - 3: Minas Gerais
        - 4: Bahia and Sergipe
        - 5: Alagoas, Ceará, Paraíba, Pernambuco, Piauí, Rio Grande do Norte
        - 6: Brasília, Goiás, Mato Grosso, Mato Grosso do Sul, Rondônia, Tocantins
        - 7: Paraná and Santa Catarina
        - 8: Rio Grande do Sul
        - 9: Acre, Amapá, Amazonas, Pará, Roraima

        Returns:
            Region code as a string (0-9).
        """
        return self[0] if len(self) >= 1 else ""

    @property
    def subregion(self) -> str:
        """
        Extract the subregion code from the CEP (first three digits).

        Returns:
            Subregion code as a string (e.g., "123" from "12345678").
        """
        return self[:3] if len(self) >= 3 else ""
