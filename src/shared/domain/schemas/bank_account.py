"""Schemas for BankAccount."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.shared.domain.models.enums import AccountType, PixKeyType


class BankInfo(BaseModel):
    """Embedded bank information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    short_name: Optional[str] = None


class BankAccountResponse(BaseModel):
    """Schema for bank account response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    # Bank account data
    agency: str
    agency_digit: Optional[str] = None
    account_number: str
    account_digit: Optional[str] = None
    account_type: AccountType

    # Holder data
    holder_name: str
    holder_document: str

    # PIX data
    pix_key_type: Optional[PixKeyType] = None
    pix_key: Optional[str] = None

    # Status
    is_primary: bool
    is_active: bool

    # Verification
    is_verified: bool = False

    # Embedded bank info
    bank: Optional[BankInfo] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
