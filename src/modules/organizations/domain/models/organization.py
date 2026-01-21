"""Organization model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index
from sqlmodel import Field, Relationship

from src.modules.organizations.domain.models.enums import OrganizationType, SharingScope
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import CNPJField, PhoneField
from src.shared.domain.models.mixins import (
    AddressMixin,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.client_contract import ClientContract
    from src.modules.organizations.domain.models.organization_membership import (
        OrganizationMembership,
    )
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess
    from src.modules.screening.domain.models.screening_template import ScreeningTemplate
    from src.modules.units.domain.models.unit import Unit
    from src.shared.domain.models.company import Company


class OrganizationBase(BaseModel):
    """Base fields for Organization."""

    name: str = Field(
        max_length=255,
        description="Organization name",
    )
    trading_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Trading/commercial name (Nome Fantasia)",
    )
    organization_type: OrganizationType = Field(
        sa_type=SAEnum(
            OrganizationType, name="organization_type", create_constraint=True
        ),
        description="Type of organization",
    )

    # Optional CNPJ (if no linked Company)
    cnpj: Optional[str] = CNPJField(
        default=None,
        nullable=True,
        description="Brazilian CNPJ (if no linked Company)",
    )

    # Contact info
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Organization email address",
    )
    phone: Optional[str] = PhoneField(
        default=None,
        nullable=True,
        description="Organization phone number (E.164 format)",
    )
    website: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Organization website URL",
    )

    # Sharing configuration for child organizations
    sharing_scope: SharingScope = Field(
        default=SharingScope.NONE,
        sa_type=SAEnum(SharingScope, name="sharing_scope", create_constraint=True),
        description="What data to share with child organizations",
    )

    # Status
    is_active: bool = Field(
        default=True,
        description="Whether the organization is currently active",
    )


class Organization(
    OrganizationBase,
    AddressMixin,
    VerificationMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    Organization table model.

    Represents a healthcare organization (hospital, clinic, outsourcing company, etc.).
    Supports one level of hierarchy: a parent organization can have children,
    but a child organization cannot have children of its own.

    The hierarchy is used for outsourcing companies that manage multiple facilities.
    Data sharing between parent and children is controlled by `sharing_scope`.
    """

    __tablename__ = "organizations"
    __table_args__ = (
        # Ensure unique CNPJ when set
        Index(
            "uq_organizations_cnpj",
            "cnpj",
            unique=True,
            postgresql_where="cnpj IS NOT NULL AND deleted_at IS NULL",
        ),
        # Note: The constraint to ensure only 1 level of depth
        # (parent organizations cannot have a parent) is enforced at application level
        # because it requires a subquery that PostgreSQL CHECK doesn't support
    )

    # Parent organization (for hierarchy)
    parent_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organizations.id",
        nullable=True,
        description="Parent organization ID (null = root organization)",
    )

    # Legal entity (optional - can use own CNPJ instead)
    company_id: Optional[UUID] = Field(
        default=None,
        foreign_key="companies.id",
        nullable=True,
        description="Linked Company for legal/financial purposes",
    )

    # Relationships
    parent: Optional["Organization"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "foreign_keys": "[Organization.parent_id]",
            "remote_side": "[Organization.id]",
        },
    )
    children: list["Organization"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "foreign_keys": "[Organization.parent_id]",
        },
    )
    company: Optional["Company"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Organization.company_id]",
            "lazy": "selectin",
        }
    )
    professionals: list["OrganizationProfessional"] = Relationship(
        back_populates="organization"
    )
    memberships: list["OrganizationMembership"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMembership.organization_id]",
        },
    )
    # Note: units, client_contracts, screening_templates, and screening_processes relationships
    # are defined on their respective models to avoid circular imports

    @property
    def is_parent(self) -> bool:
        """Check if this organization is a parent (has no parent_id)."""
        return self.parent_id is None

    @property
    def is_child(self) -> bool:
        """Check if this organization is a child (has parent_id)."""
        return self.parent_id is not None

    def can_have_children(self) -> bool:
        """
        Check if this organization can have child organizations.

        Only root organizations (without parent) can have children.
        This enforces a maximum of 1 level of depth.
        """
        return self.parent_id is None
