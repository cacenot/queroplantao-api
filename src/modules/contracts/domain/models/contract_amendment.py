"""ContractAmendment model - modifications to existing contracts."""

from datetime import date
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import JSON, Index
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.contract_document import ContractDocument
    from src.modules.contracts.domain.models.professional_contract import (
        ProfessionalContract,
    )


class ContractAmendmentBase(BaseModel):
    """Base fields for ContractAmendment."""

    amendment_number: int = Field(
        ge=1,
        description="Sequential amendment number for this contract",
    )
    description: str = Field(
        max_length=2000,
        description="Description of what changed in this amendment",
    )

    # Snapshot of changes (flexible JSON storage)
    previous_values: Optional[dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="JSON snapshot of values before amendment",
    )
    new_values: Optional[dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="JSON snapshot of new values after amendment",
    )

    # When the amendment takes effect
    effective_from: date = Field(
        description="Date when the amendment becomes effective",
    )

    # Notes
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Additional notes about the amendment",
    )


class ContractAmendment(
    ContractAmendmentBase,
    VerificationMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ContractAmendment table model.

    Represents a modification (aditivo contratual) to an existing professional contract.
    Amendments track changes to contract terms such as hourly rate, work location,
    contract period, etc.

    Each amendment stores:
    - description: What changed
    - previous_values/new_values: JSON snapshots for audit trail
    - effective_from: When the changes take effect
    - Signature timestamps for approval workflow

    Amendments are numbered sequentially per contract (amendment_number).
    The combination of (contract_id, amendment_number) is unique.
    """

    __tablename__ = "contract_amendments"
    __table_args__ = (
        # Unique amendment number per contract
        Index(
            "uq_contract_amendments_contract_number",
            "contract_id",
            "amendment_number",
            unique=True,
        ),
        # Index for listing amendments by contract
        Index("ix_contract_amendments_contract_id", "contract_id"),
        # Index for filtering by effective date
        Index("ix_contract_amendments_effective_from", "effective_from"),
    )

    # Contract reference (required)
    contract_id: UUID = Field(
        foreign_key="professional_contracts.id",
        nullable=False,
        description="Contract being amended",
    )

    # Signature workflow timestamps
    professional_signed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When professional signed the amendment",
    )
    organization_signed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When organization signed the amendment",
    )

    # Relationships
    contract: "ProfessionalContract" = Relationship(back_populates="amendments")
    documents: list["ContractDocument"] = Relationship(back_populates="amendment")

    @property
    def is_fully_signed(self) -> bool:
        """Check if amendment has been signed by both parties."""
        return (
            self.professional_signed_at is not None
            and self.organization_signed_at is not None
        )
