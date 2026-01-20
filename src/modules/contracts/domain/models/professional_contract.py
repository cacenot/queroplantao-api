"""ProfessionalContract model - contracts between organization and professionals."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum, Index
from sqlmodel import Field, Relationship

from src.modules.contracts.domain.models.enums import ContractStatus
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
    VersionMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.client_contract import ClientContract
    from src.modules.contracts.domain.models.contract_amendment import (
        ContractAmendment,
    )
    from src.modules.contracts.domain.models.contract_document import ContractDocument
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess
    from src.modules.units.domain.models.unit import Unit
    from src.shared.domain.models.bank_account import BankAccount
    from src.shared.domain.models.company import Company


class ProfessionalContractBase(BaseModel):
    """Base fields for ProfessionalContract."""

    contract_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Contract number/identifier",
    )
    status: ContractStatus = Field(
        default=ContractStatus.DRAFT,
        sa_type=SAEnum(ContractStatus, name="contract_status", create_constraint=True),
        description="Contract status",
    )

    # Financial terms
    hourly_rate: Optional[Decimal] = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        description="Hourly rate value",
    )
    currency: str = Field(
        default="BRL",
        max_length=3,
        description="Currency code (ISO 4217)",
    )

    # Validity period
    start_date: Optional[date] = Field(
        default=None,
        description="Contract start date",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Contract end date (NULL = indefinite)",
    )

    # Notes
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Additional notes about the contract",
    )


class ProfessionalContract(
    ProfessionalContractBase,
    TrackingMixin,
    VersionMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    ProfessionalContract table model.

    Represents a contract between the organization and a professional.
    Contains detailed information about employment terms, work location,
    payment details, and signature workflow.

    Key relationships:
    - organization_professional: The professional being contracted
    - client_contract: Optional parent contract (if working under a client engagement)
    - company: Professional's company/PJ (for service provision contracts)
    - bank_account: Payment destination
    - unit: Work location where the professional will perform activities

    Signature workflow:
    - submitted_at: When contract was sent for signatures
    - professional_signed_at: When professional signed
    - organization_signed_at: When organization signed

    Termination:
    - terminated_at: When contract was terminated
    - terminated_by: Who terminated the contract
    - termination_reason: Reason for termination
    - termination_notice_date: Date when termination notice was given
    """

    __tablename__ = "professional_contracts"
    __table_args__ = (
        # Unique contract number per professional (when set and not soft-deleted)
        Index(
            "uq_professional_contracts_prof_number",
            "organization_professional_id",
            "contract_number",
            unique=True,
            postgresql_where="contract_number IS NOT NULL AND deleted_at IS NULL",
        ),
        # Index for listing contracts by professional
        Index(
            "ix_professional_contracts_org_professional_id",
            "organization_professional_id",
        ),
        # Index for filtering by status
        Index("ix_professional_contracts_status", "status"),
        # Index for filtering by client contract
        Index("ix_professional_contracts_client_contract_id", "client_contract_id"),
        # Index for filtering by unit
        Index("ix_professional_contracts_unit_id", "unit_id"),
    )

    # Core relationships (professional is required)
    organization_professional_id: UUID = Field(
        foreign_key="organization_professionals.id",
        nullable=False,
        description="Professional being contracted",
    )

    # Optional parent contract (client engagement)
    client_contract_id: Optional[UUID] = Field(
        default=None,
        foreign_key="client_contracts.id",
        nullable=True,
        description="Parent client contract (if working under a client engagement)",
    )

    # Professional's company (for PJ contracts)
    company_id: Optional[UUID] = Field(
        default=None,
        foreign_key="companies.id",
        nullable=True,
        description="Professional's company (for PJ service provision)",
    )

    # Payment destination
    bank_account_id: Optional[UUID] = Field(
        default=None,
        foreign_key="bank_accounts.id",
        nullable=True,
        description="Bank account for payments",
    )

    # Work location
    unit_id: Optional[UUID] = Field(
        default=None,
        foreign_key="units.id",
        nullable=True,
        description="Work location (unit)",
    )

    # Signature workflow timestamps
    submitted_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When contract was submitted for signatures",
    )
    professional_signed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When professional signed the contract",
    )
    organization_signed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When organization signed the contract",
    )

    # Termination fields
    terminated_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When contract was terminated",
    )
    terminated_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who terminated the contract",
    )
    termination_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Reason for contract termination",
    )
    termination_notice_date: Optional[date] = Field(
        default=None,
        description="Date when termination notice was given",
    )

    # Relationships
    organization_professional: "OrganizationProfessional" = Relationship(
        back_populates="contracts"
    )
    client_contract: Optional["ClientContract"] = Relationship(
        back_populates="professional_contracts"
    )
    company: Optional["Company"] = Relationship(back_populates="professional_contracts")
    bank_account: Optional["BankAccount"] = Relationship(
        back_populates="professional_contracts"
    )
    unit: Optional["Unit"] = Relationship(back_populates="professional_contracts")
    amendments: list["ContractAmendment"] = Relationship(back_populates="contract")
    documents: list["ContractDocument"] = Relationship(back_populates="contract")
    screening_processes: list["ScreeningProcess"] = Relationship(
        back_populates="professional_contract"
    )

    @property
    def is_pending_signatures(self) -> bool:
        """Check if contract is waiting for signatures."""
        return self.submitted_at is not None and (
            self.professional_signed_at is None or self.organization_signed_at is None
        )

    @property
    def is_fully_signed(self) -> bool:
        """Check if contract has been signed by both parties."""
        return (
            self.professional_signed_at is not None
            and self.organization_signed_at is not None
        )

    @property
    def is_terminated(self) -> bool:
        """Check if contract has been terminated."""
        return self.terminated_at is not None
