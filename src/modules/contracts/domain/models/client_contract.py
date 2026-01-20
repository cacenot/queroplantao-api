"""ClientContract model - contracts between organization and external clients."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index
from sqlmodel import Field, Relationship

from src.modules.contracts.domain.models.enums import ContractStatus
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.professional_contract import (
        ProfessionalContract,
    )
    from src.modules.organizations.domain.models.organization import Organization


class ClientContractBase(BaseModel):
    """Base fields for ClientContract."""

    client_name: str = Field(
        max_length=255,
        description="Name of the client (hospital, municipality, etc.)",
    )
    contract_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Contract or bidding number",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Contract description and details",
    )
    status: ContractStatus = Field(
        default=ContractStatus.DRAFT,
        sa_type=SAEnum(ContractStatus, name="contract_status", create_constraint=True),
        description="Contract status",
    )


class ClientContract(
    ClientContractBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    ClientContract table model.

    Represents a "parent" contract between the organization and an external client.
    These are typically contracts with hospitals, municipalities (via public bidding),
    or other healthcare facilities that hire the organization's services.

    This is a simplified contract model used mainly for:
    - Tracking where professionals are being allocated
    - Grouping professional contracts under a common client relationship
    - Basic record of external business relationships

    Professional contracts can optionally reference a ClientContract to indicate
    which client engagement they are part of.
    """

    __tablename__ = "client_contracts"
    __table_args__ = (
        # Unique contract number per organization (when set and not soft-deleted)
        Index(
            "uq_client_contracts_org_number",
            "organization_id",
            "contract_number",
            unique=True,
            postgresql_where="contract_number IS NOT NULL AND deleted_at IS NULL",
        ),
        # Index for listing contracts by organization
        Index("ix_client_contracts_organization_id", "organization_id"),
        # Index for filtering by status
        Index("ix_client_contracts_status", "status"),
    )

    # Organization reference (required - tenant isolation)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization that owns this contract",
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="client_contracts")
    professional_contracts: list["ProfessionalContract"] = Relationship(
        back_populates="client_contract"
    )
