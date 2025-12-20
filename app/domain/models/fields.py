"""Custom field helpers for SQLModel."""

from typing import Any, Optional

from sqlmodel import DateTime, Field


def AwareDatetimeField(
    default: Any = ...,
    *,
    default_factory: Optional[Any] = None,
    nullable: bool = True,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Create a timezone-aware datetime field for SQLModel.

    Automatically configures DateTime(timezone=True) for TIMESTAMP WITH TIME ZONE storage.
    Use with Pydantic's AwareDatetime type annotation for validation.

    Args:
        default: Default value for the field
        default_factory: Factory function for default value
        nullable: Whether the field can be NULL in database (default: True)
        description: Field description for OpenAPI docs
        **kwargs: Additional Field parameters (e.g., sa_column_kwargs)

    Returns:
        Field configured for timezone-aware datetime storage

    Example:
        ```python
        from pydantic import AwareDatetime
        from app.domain.models.fields import AwareDatetimeField

        class Project(ProjectBase, table=True):
            __tablename__ = "projects"

            delivery_date: Optional[AwareDatetime] = AwareDatetimeField(
                default=None,
                description="Expected delivery date (UTC)",
            )
        ```
    """
    return Field(
        default=default,
        default_factory=default_factory,
        sa_type=DateTime(timezone=True),
        nullable=nullable,
        description=description,
        **kwargs,
    )


def PhoneField(
    *,
    default: Any = ...,
    default_factory: Optional[Any] = None,
    nullable: bool = False,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Create a phone number field for SQLModel with automatic validation.

    Validates and normalizes to E.164 format, storing internationally.
    Automatically adds OpenAPI schema documentation.

    Args:
        default: Default value for the field
        default_factory: Factory function for default value
        nullable: Whether the field can be NULL in database (default: False)
        description: Field description for OpenAPI docs
        **kwargs: Additional Field parameters

    Returns:
        Field configured for phone validation and storage

    Example:
        ```python
        class Customer(CustomerBase, table=True):
            phone: Optional[str] = PhoneField(
                nullable=True,
                description="Customer phone number (E.164 format)"
            )
        ```
    """
    return Field(
        default=default,
        default_factory=default_factory,
        max_length=20,  # Sufficient for E.164 (up to + followed by 15 digits)
        nullable=nullable,
        description=description or "International phone number in E.164 format",
        **kwargs,
    )


def CPFField(
    *,
    default: Any = ...,
    default_factory: Optional[Any] = None,
    nullable: bool = False,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Create a CPF field for SQLModel with automatic validation.

    Validates and normalizes CPF numbers, storing digits only.
    Automatically adds OpenAPI schema documentation.

    Args:
        default: Default value for the field
        default_factory: Factory function for default value
        nullable: Whether the field can be NULL in database (default: False)
        description: Field description for OpenAPI docs
        **kwargs: Additional Field parameters

    Returns:
        Field configured for CPF validation and storage

    Example:
        ```python
        class Customer(CustomerBase, table=True):
            cpf: str = CPFField(
                description="Customer CPF (digits only)"
            )
        ```
    """
    return Field(
        default=default,
        default_factory=default_factory,
        max_length=11,
        nullable=nullable,
        description=description or "Brazilian CPF number (11 digits, no formatting)",
        **kwargs,
    )


def CNPJField(
    *,
    default: Any = ...,
    default_factory: Optional[Any] = None,
    nullable: bool = False,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Create a CNPJ field for SQLModel with automatic validation.

    Validates and normalizes CNPJ numbers, storing digits only.
    Automatically adds OpenAPI schema documentation.

    Args:
        default: Default value for the field
        default_factory: Factory function for default value
        nullable: Whether the field can be NULL in database (default: False)
        description: Field description for OpenAPI docs
        **kwargs: Additional Field parameters

    Returns:
        Field configured for CNPJ validation and storage

    Example:
        ```python
        class Company(CompanyBase, table=True):
            cnpj: str = CNPJField(
                description="Company CNPJ (digits only)"
            )
        ```
    """
    return Field(
        default=default,
        default_factory=default_factory,
        max_length=14,
        nullable=nullable,
        description=description or "Brazilian CNPJ number (14 digits, no formatting)",
        **kwargs,
    )


def CPFOrCNPJField(
    *,
    default: Any = ...,
    default_factory: Optional[Any] = None,
    nullable: bool = False,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Create a CPF or CNPJ field for SQLModel with automatic detection and validation.

    Automatically detects whether input is CPF (11 digits) or CNPJ (14 digits),
    validates accordingly, and normalizes to digits only.
    Automatically adds OpenAPI schema documentation.

    Args:
        default: Default value for the field
        default_factory: Factory function for default value
        nullable: Whether the field can be NULL in database (default: False)
        description: Field description for OpenAPI docs
        **kwargs: Additional Field parameters

    Returns:
        Field configured for CPF/CNPJ validation and storage

    Example:
        ```python
        class Customer(CustomerBase, table=True):
            cpf_cnpj: str = CPFOrCNPJField(
                description="Customer CPF or CNPJ (digits only)"
            )
        ```
    """
    return Field(
        default=default,
        default_factory=default_factory,
        max_length=14,
        nullable=nullable,
        description=description
        or "Brazilian CPF (11 digits) or CNPJ (14 digits), no formatting",
        **kwargs,
    )
