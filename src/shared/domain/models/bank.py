"""Bank model for reference data."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import PrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from src.shared.domain.models.bank_account import BankAccount


class BankBase(BaseModel):
    """Base fields for Bank."""

    code: str = Field(
        max_length=10,
        description="Bank code (COMPE code, e.g., '001' for Banco do Brasil)",
    )
    ispb_code: Optional[str] = Field(
        default=None,
        max_length=8,
        description="ISPB code (8 digits)",
    )
    name: str = Field(
        max_length=255,
        description="Bank full name",
    )
    short_name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Bank short/commercial name",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the bank is currently active",
    )


class Bank(
    BankBase,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    Bank table model.

    Reference table for Brazilian banks (BACEN regulated).
    Will be populated via migration with all active banks.
    """

    __tablename__ = "banks"
    __table_args__ = (
        UniqueConstraint("code", name="uq_banks_code"),
        UniqueConstraint("ispb_code", name="uq_banks_ispb_code"),
    )

    # Relationships
    accounts: list["BankAccount"] = Relationship(back_populates="bank")
