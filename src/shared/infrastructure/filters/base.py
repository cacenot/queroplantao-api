"""Base custom filters for the application."""

from enum import Enum
from typing import Any, Generic, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column
from sqlalchemy.sql.elements import ColumnElement

from src.app.exceptions import ValidationError

T = TypeVar("T")


class ExcludeListFilter(BaseModel, Generic[T]):
    """
    Exclude list filter (NOT IN clause) with automatic type validation.

    Similar to ListFilter but generates a NOT IN clause instead of IN.
    Useful for excluding specific values from results.

    Examples:
        - ExcludeListFilter[str]: Excludes strings
        - ExcludeListFilter[DocumentCategory]: Excludes specific categories
        - exclude_categories=["SPECIALTY"] -> category NOT IN ('SPECIALTY')
    """

    values: list[T] | None = Field(
        default=None, description="List of values for NOT IN clause"
    )

    @field_validator("values", mode="before")
    @classmethod
    def validate_values(cls, v: Any) -> list[Any] | None:
        """
        Validate list values based on generic type T.

        Supports:
        - Native types: str, int, float, bool, UUID
        - Enum types: Validates against enum values and converts strings to enum instances
        """
        if v is None:
            return None

        # Get the generic type from __pydantic_generic_metadata__
        generic_args = getattr(cls, "__pydantic_generic_metadata__", {}).get("args", ())
        if not generic_args:
            # Fallback: try to get from model fields (Pydantic v2)
            field_info = cls.model_fields.get("values")
            if field_info and hasattr(field_info, "annotation"):
                import typing

                if hasattr(typing, "get_args"):
                    inner_args = typing.get_args(field_info.annotation)
                    if inner_args:
                        # Extract T from Optional[List[T]]
                        if typing.get_origin(inner_args[0]) is list:
                            generic_args = typing.get_args(inner_args[0])

        if not generic_args:
            # No type info available, return as-is
            return list(v) if v else None

        value_type = generic_args[0]

        # Handle List[T] - extract T
        if hasattr(value_type, "__origin__"):
            import typing

            if typing.get_origin(value_type) is list:
                value_type = typing.get_args(value_type)[0]

        validated_values: list[Any] = []
        invalid_values: list[Any] = []

        for item in v:
            # If already correct type, keep it
            if isinstance(item, value_type):
                validated_values.append(item)
                continue

            # Try to convert/validate
            try:
                # Enum validation
                if isinstance(value_type, type) and issubclass(value_type, Enum):
                    converted = value_type(item)
                    validated_values.append(converted)
                # UUID validation
                elif value_type is UUID:
                    if isinstance(item, str):
                        validated_values.append(UUID(item))
                    else:
                        invalid_values.append(item)
                # Native types (str, int, float, bool)
                elif value_type in (str, int, float, bool):
                    converted = value_type(item)
                    validated_values.append(converted)
                else:
                    # Unknown type, try direct construction
                    converted = value_type(item)
                    validated_values.append(converted)
            except (ValueError, TypeError, KeyError):
                invalid_values.append(item)

        # Raise error if any invalid values
        if invalid_values:
            # Build error message based on type
            if isinstance(value_type, type) and issubclass(value_type, Enum):
                valid_values = [e.value for e in value_type]
                raise ValidationError(
                    message=(
                        f"Invalid values for {value_type.__name__}. "
                        f"Must be one of: {', '.join(map(str, valid_values))}"
                    ),
                    details={
                        "field": "values",
                        "invalid_values": invalid_values,
                        "valid_values": valid_values,
                        "type": value_type.__name__,
                    },
                )
            else:
                raise ValidationError(
                    message=f"Invalid values. Expected type: {value_type.__name__}",
                    details={
                        "field": "values",
                        "invalid_values": invalid_values,
                        "expected_type": value_type.__name__,
                    },
                )

        return validated_values if validated_values else None

    def is_active(self) -> bool:
        """Check if filter has values."""
        return self.values is not None and len(self.values) > 0

    def to_sqlalchemy(self, column: Column[Any]) -> ColumnElement[bool] | None:
        """Convert to SQLAlchemy NOT IN clause."""
        if not self.is_active():
            return None

        return ~column.in_(cast("list[T]", self.values))


__all__ = ["ExcludeListFilter"]
