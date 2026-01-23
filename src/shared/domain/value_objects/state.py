"""Brazilian state (UF) value object with validation."""

from typing import Any

from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema

from src.app.i18n import ValidationMessages, get_message

# Brazilian states mapping: UF code -> full name
BRAZILIAN_STATES: dict[str, str] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Valid UF codes set for fast lookup
VALID_UF_CODES: set[str] = set(BRAZILIAN_STATES.keys())


class StateUF(str):
    """
    Brazilian state code (UF) string type with validation.

    Automatically validates and normalizes state codes.
    Stores uppercase 2-letter code.

    Example:
        StateUF("sp") → "SP"
        StateUF("SP") → "SP"
        StateUF("XX") → raises ValueError
    """

    def __new__(cls, value: str) -> "StateUF":
        """Validate and normalize on instantiation."""
        if isinstance(value, cls):
            return value
        return cls._validate(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Define Pydantic schema for state validation."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, value: str) -> "StateUF":
        """Validate and normalize state code (UF)."""
        if not isinstance(value, str):
            raise ValueError(get_message(ValidationMessages.UF_MUST_BE_STRING))

        # Normalize: strip whitespace and convert to uppercase
        normalized = value.strip().upper()

        # Validate length
        if len(normalized) != 2:
            raise ValueError(
                get_message(
                    ValidationMessages.UF_INVALID_LENGTH, length=len(normalized)
                )
            )

        # Validate if it's a valid Brazilian state
        if normalized not in VALID_UF_CODES:
            raise ValueError(
                get_message(ValidationMessages.UF_INVALID_CODE, code=normalized)
            )

        return str.__new__(cls, normalized)  # Avoid recursion

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """JSON schema for OpenAPI documentation."""
        json_schema = handler(schema)
        json_schema.update(
            {
                "type": "string",
                "pattern": "^[A-Z]{2}$",
                "enum": sorted(VALID_UF_CODES),
                "example": "SP",
                "description": "Brazilian state code (UF) - 2 uppercase letters",
            }
        )
        return json_schema

    @property
    def full_name(self) -> str:
        """
        Return the full name of the state.

        Returns:
            Full state name in Portuguese (e.g., "São Paulo" for "SP").
        """
        return BRAZILIAN_STATES.get(self, "")

    @property
    def region(self) -> str:
        """
        Return the region of the state.

        Returns:
            Region name in Portuguese.
        """
        regions: dict[str, str] = {
            # Norte
            "AC": "Norte",
            "AP": "Norte",
            "AM": "Norte",
            "PA": "Norte",
            "RO": "Norte",
            "RR": "Norte",
            "TO": "Norte",
            # Nordeste
            "AL": "Nordeste",
            "BA": "Nordeste",
            "CE": "Nordeste",
            "MA": "Nordeste",
            "PB": "Nordeste",
            "PE": "Nordeste",
            "PI": "Nordeste",
            "RN": "Nordeste",
            "SE": "Nordeste",
            # Centro-Oeste
            "DF": "Centro-Oeste",
            "GO": "Centro-Oeste",
            "MT": "Centro-Oeste",
            "MS": "Centro-Oeste",
            # Sudeste
            "ES": "Sudeste",
            "MG": "Sudeste",
            "RJ": "Sudeste",
            "SP": "Sudeste",
            # Sul
            "PR": "Sul",
            "RS": "Sul",
            "SC": "Sul",
        }
        return regions.get(self, "")

    @classmethod
    def get_all_states(cls) -> dict[str, str]:
        """
        Return all Brazilian states.

        Returns:
            Dictionary mapping UF codes to full names.
        """
        return BRAZILIAN_STATES.copy()

    @classmethod
    def get_states_by_region(cls, region: str) -> list["StateUF"]:
        """
        Return all states in a given region.

        Args:
            region: Region name (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

        Returns:
            List of StateUF objects in the region.
        """
        region_states: dict[str, list[str]] = {
            "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
            "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
            "Centro-Oeste": ["DF", "GO", "MT", "MS"],
            "Sudeste": ["ES", "MG", "RJ", "SP"],
            "Sul": ["PR", "RS", "SC"],
        }
        return [cls(uf) for uf in region_states.get(region, [])]
