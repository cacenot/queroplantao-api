"""
Base models e mixins compartilhados.
"""

from src.shared.domain.models.base import (
    BaseModel,
    NAMING_CONVENTION,
    metadata,
)
from src.shared.domain.models.bank import Bank, BankBase
from src.shared.domain.models.bank_account import BankAccount, BankAccountBase
from src.shared.domain.models.company import Company, CompanyBase
from src.shared.domain.models.enums import AccountType, PixKeyType
from src.shared.domain.models.fields import (
    AwareDatetimeField,
    CNPJField,
    CPFField,
    CPFOrCNPJField,
    PhoneField,
)
from src.shared.domain.models.mixins import (
    AddressMixin,
    MetadataMixin,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
    VersionMixin,
)

__all__ = [
    # Base models
    "BaseModel",
    "NAMING_CONVENTION",
    "metadata",
    # Shared models
    "Bank",
    "BankBase",
    "BankAccount",
    "BankAccountBase",
    "Company",
    "CompanyBase",
    # Shared enums
    "AccountType",
    "PixKeyType",
    # Fields
    "AwareDatetimeField",
    "CNPJField",
    "CPFField",
    "CPFOrCNPJField",
    "PhoneField",
    # Mixins
    "AddressMixin",
    "MetadataMixin",
    "PrimaryKeyMixin",
    "SoftDeleteMixin",
    "TimestampMixin",
    "TrackingMixin",
    "VerificationMixin",
    "VersionMixin",
]
