"""Company model for legal entities."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import CNPJField, PhoneField
from src.shared.domain.models.mixins import (
    AddressMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.professional_contract import (
        ProfessionalContract,
    )
    from src.modules.professionals.domain.models.professional_company import (
        ProfessionalCompany,
    )
    from src.modules.units.domain.models.unit import Unit
    from src.shared.domain.models.bank_account import BankAccount


class CompanyBase(BaseModel):
    """Base fields for Company."""

    # Legal identification
    cnpj: str = CNPJField(
        description="Brazilian CNPJ (14 digits, no formatting)",
    )
    legal_name: str = Field(
        max_length=255,
        description="Legal/registered company name (Razão Social)",
    )
    trade_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Trade/commercial name (Nome Fantasia)",
    )

    # Registration data
    state_registration: Optional[str] = Field(
        default=None,
        max_length=30,
        description="State registration number (Inscrição Estadual)",
    )
    municipal_registration: Optional[str] = Field(
        default=None,
        max_length=30,
        description="Municipal registration number (Inscrição Municipal)",
    )

    # Contact data
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Company email address",
    )
    phone: Optional[str] = PhoneField(
        default=None,
        nullable=True,
        description="Company phone number (E.164 format)",
    )

    # Status
    is_active: bool = Field(
        default=True,
        description="Whether the company is currently active",
    )


class Company(
    CompanyBase,
    AddressMixin,
    VerificationMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    Company table model.

    Stores legal entities (empresas) used for contracting and payments.
    Can be used by professionals (their own company for receiving payments)
    or by organizations (the contracting entity).
    """

    __tablename__ = "companies"
    __table_args__ = (UniqueConstraint("cnpj", name="uq_companies_cnpj"),)

    # Relationships
    professional_companies: list["ProfessionalCompany"] = Relationship(
        back_populates="company"
    )
    bank_accounts: list["BankAccount"] = Relationship(back_populates="company")
    # Note: units and professional_contracts relationships are defined on Unit and ProfessionalContract
    # to avoid circular import issues
