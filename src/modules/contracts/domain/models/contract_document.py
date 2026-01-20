"""ContractDocument model - file attachments for contracts and amendments."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.contract_amendment import (
        ContractAmendment,
    )
    from src.modules.contracts.domain.models.professional_contract import (
        ProfessionalContract,
    )


class ContractDocumentBase(BaseModel):
    """Base fields for ContractDocument."""

    # File information
    file_url: str = Field(
        max_length=2048,
        description="URL to the uploaded file",
    )
    file_name: str = Field(
        max_length=255,
        description="Original file name",
    )
    file_size: Optional[int] = Field(
        default=None,
        description="File size in bytes",
    )
    mime_type: Optional[str] = Field(
        default=None,
        max_length=100,
        description="MIME type of the file",
    )

    # Notes
    notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional notes about the document",
    )


class ContractDocument(
    ContractDocumentBase,
    VerificationMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ContractDocument table model.

    Represents a file attachment associated with a contract or amendment.
    Used for storing signed contracts, amendment documents, termination notices, etc.

    Each document is linked to:
    - contract_id: The professional contract (required)
    - amendment_id: Specific amendment (optional, if document is amendment-specific)

    Verification:
    - Uses VerificationMixin to track document verification status
    - verified_at/verified_by indicate when/who verified the document
    """

    __tablename__ = "contract_documents"
    __table_args__ = (
        # Index for listing documents by contract
        Index("ix_contract_documents_contract_id", "contract_id"),
        # Index for listing documents by amendment
        Index("ix_contract_documents_amendment_id", "amendment_id"),
    )

    # Contract reference (required)
    contract_id: UUID = Field(
        foreign_key="professional_contracts.id",
        nullable=False,
        description="Contract this document belongs to",
    )

    # Amendment reference (optional - if document is amendment-specific)
    amendment_id: Optional[UUID] = Field(
        default=None,
        foreign_key="contract_amendments.id",
        nullable=True,
        description="Amendment this document belongs to (if applicable)",
    )

    # Relationships
    contract: "ProfessionalContract" = Relationship(back_populates="documents")
    amendment: Optional["ContractAmendment"] = Relationship(back_populates="documents")
