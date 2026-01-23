"""Contact-related value objects with validation."""

from typing import Any, Optional

import phonenumbers
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema

from src.app.i18n import ValidationMessages, get_message


class Phone(str):
    """
    International phone number string type with validation.

    Automatically validates and normalizes phone numbers to E.164 format.
    Stores in international format (e.g., +15551234567) in the database.

    Example:
        Phone("+1 (555) 123-4567") → "+15551234567"
    """

    def __new__(cls, value: str) -> "Phone":
        """Validate and normalize on instantiation."""
        if isinstance(value, cls):
            return value
        return cls._validate(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Define Pydantic schema for phone validation."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, value: str) -> "Phone":
        """Validate and normalize phone number."""
        if not isinstance(value, str):
            raise ValueError(get_message(ValidationMessages.PHONE_MUST_BE_STRING))

        try:
            parsed = phonenumbers.parse(value, None)  # Auto-detect region
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError(get_message(ValidationMessages.PHONE_INVALID))
            normalized = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
            return str.__new__(cls, normalized)  # Avoid recursion
        except phonenumbers.NumberParseException as e:
            raise ValueError(
                get_message(ValidationMessages.PHONE_INVALID_FORMAT, error=str(e))
            )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """JSON schema for OpenAPI documentation."""
        json_schema = handler(schema)
        json_schema.update(
            {
                "type": "string",
                "pattern": r"^\+[1-9]\d{1,14}$",  # E.164 regex
                "example": "+15551234567",
                "description": "International phone number in E.164 format (e.g., +15551234567)",
            }
        )
        return json_schema

    @property
    def ddi(self) -> str:
        """
        Extract the DDI (country code) from the E.164 phone number.

        Returns:
            Country code as a string (e.g., "55" for Brazil).

        Raises:
            ValueError: If the phone number cannot be parsed.
        """
        try:
            parsed = phonenumbers.parse(self, None)
            return str(parsed.country_code)
        except phonenumbers.NumberParseException:
            raise ValueError(
                get_message(ValidationMessages.PHONE_UNABLE_TO_EXTRACT_DDI, phone=self)
            )

    @property
    def ddd(self) -> Optional[str]:
        """
        Extract the DDD (area code) from the E.164 phone number.

        Returns:
            Area code as a string if available (e.g., "11" for São Paulo), or None if not applicable.

        Raises:
            ValueError: If the phone number cannot be parsed.
        """
        try:
            parsed = phonenumbers.parse(self, None)
            # Area code is not always present; return None if not available
            if (
                parsed.national_number and len(str(parsed.national_number)) > 7
            ):  # Rough check for area code presence
                # For countries with area codes, extract it (this is a simplified approach)
                # phonenumbers doesn't always separate area code explicitly, so we may need custom logic per country
                # For Brazil (DDI 55), area code is typically 2 digits after country code
                if parsed.country_code == 55 and len(str(parsed.national_number)) >= 10:
                    return str(parsed.national_number)[:2]
                # Add similar logic for other countries as needed
            return None
        except phonenumbers.NumberParseException:
            raise ValueError(
                get_message(ValidationMessages.PHONE_UNABLE_TO_EXTRACT_DDD, phone=self)
            )

    @property
    def formatted_national(self) -> str:
        """
        Return the phone number in national format for display.

        Returns:
            Formatted national number (e.g., "(11) 98765-4321" for Brazil).

        Raises:
            ValueError: If the phone number cannot be parsed.
        """
        try:
            parsed = phonenumbers.parse(self, None)
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.NATIONAL
            )
        except phonenumbers.NumberParseException:
            raise ValueError(
                get_message(ValidationMessages.PHONE_UNABLE_TO_FORMAT, phone=self)
            )
