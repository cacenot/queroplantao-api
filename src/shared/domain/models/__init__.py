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
from src.shared.domain.models.document_type import (
    DocumentCategory,
    DocumentType,
    DocumentTypeBase,
)
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
from src.shared.domain.models.specialty import Specialty, SpecialtyBase

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
    "DocumentCategory",
    "DocumentType",
    "DocumentTypeBase",
    "Specialty",
    "SpecialtyBase",
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
