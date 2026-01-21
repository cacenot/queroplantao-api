"""BankAccount model for storing payment information."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.enums import AccountType, PixKeyType
from src.shared.domain.models.fields import CPFOrCNPJField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.professional_contract import (
        ProfessionalContract,
    )
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.shared.domain.models.bank import Bank
    from src.shared.domain.models.company import Company


class BankAccountBase(BaseModel):
    """Base fields for BankAccount."""

    # Bank account data
    agency: str = Field(
        max_length=10,
        description="Bank agency number",
    )
    agency_digit: Optional[str] = Field(
        default=None,
        max_length=2,
        description="Agency verification digit",
    )
    account_number: str = Field(
        max_length=20,
        description="Account number",
    )
    account_digit: Optional[str] = Field(
        default=None,
        max_length=2,
        description="Account verification digit",
    )
    account_type: AccountType = Field(
        default=AccountType.CHECKING,
        sa_type=SAEnum(AccountType, name="account_type", create_constraint=True),
        description="Account type: CHECKING or SAVINGS",
    )

    # Holder data
    holder_name: str = Field(
        max_length=255,
        description="Account holder name",
    )
    holder_document: str = CPFOrCNPJField(
        description="Account holder document (CPF or CNPJ)",
    )

    # PIX data (optional)
    pix_key_type: Optional[PixKeyType] = Field(
        default=None,
        sa_type=SAEnum(PixKeyType, name="pix_key_type", create_constraint=True),
        description="Type of PIX key",
    )
    pix_key: Optional[str] = Field(
        default=None,
        max_length=255,
        description="PIX key value",
    )

    # Status flags
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary account for the owner",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the account is currently active",
    )


class BankAccount(
    BankAccountBase,
    VerificationMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    BankAccount table model.

    Stores bank account information for payments.
    Can be linked to either a professional directly or to a company.
    Only one of professional_id or company_id should be set (enforced by constraint).

    Constraints:
    - At least one owner (professional_id or company_id) must be set
    - Only one primary account per owner (partial unique index)
    """

    __tablename__ = "bank_accounts"
    __table_args__ = (
        # Ensure at least one owner is set
        CheckConstraint(
            "(organization_professional_id IS NOT NULL AND company_id IS NULL) OR "
            "(organization_professional_id IS NULL AND company_id IS NOT NULL)",
            name="ck_bank_accounts_owner",
        ),
        # Only one primary account per organization professional
        Index(
            "uq_bank_accounts_org_professional_primary",
            "organization_professional_id",
            unique=True,
            postgresql_where="is_primary = true AND organization_professional_id IS NOT NULL",
        ),
        # Only one primary account per company
        Index(
            "uq_bank_accounts_company_primary",
            "company_id",
            unique=True,
            postgresql_where="is_primary = true AND company_id IS NOT NULL",
        ),
        # Unique constraint for bank + agency + account per owner
        UniqueConstraint(
            "bank_id",
            "agency",
            "account_number",
            "organization_professional_id",
            name="uq_bank_accounts_org_professional_account",
        ),
        UniqueConstraint(
            "bank_id",
            "agency",
            "account_number",
            "company_id",
            name="uq_bank_accounts_company_account",
        ),
    )

    # Foreign keys
    bank_id: UUID = Field(
        foreign_key="banks.id",
        nullable=False,
        description="Bank reference ID",
    )
    organization_professional_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organization_professionals.id",
        nullable=True,
        description="Organization professional ID (if directly owned by professional)",
    )
    company_id: Optional[UUID] = Field(
        default=None,
        foreign_key="companies.id",
        nullable=True,
        description="Company ID (if owned by company)",
    )

    # Relationships
    bank: "Bank" = Relationship(back_populates="accounts")
    professional: Optional["OrganizationProfessional"] = Relationship(
        back_populates="bank_accounts"
    )
    company: Optional["Company"] = Relationship(back_populates="bank_accounts")
    # Note: professional_contracts relationship is defined via ProfessionalContract.bank_account
    # to avoid circular import issues
