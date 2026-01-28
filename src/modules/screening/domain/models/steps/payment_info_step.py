"""Payment info step - bank account and optional company data collection."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import StepType
from src.modules.screening.domain.models.steps.base_step import ScreeningStepMixin
from src.shared.domain.models.base import BaseModel

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_version import (
        ProfessionalVersion,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class PaymentInfoStepBase(BaseModel):
    """
    Payment info step fields.

    This step collects payment-related data:
    - Bank account (required) - where the professional receives payments
    - Company data (optional) - only if professional operates as PJ

    The step is optional in the screening flow, placed after document review.
    """

    # Is professional operating as PJ (empresa)?
    is_pj: bool = Field(
        default=False,
        description="Whether professional operates as PJ (empresa)",
    )

    # Reference to the created/updated bank account
    bank_account_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="ID of the BankAccount record created/updated",
    )

    # References to company records (only if is_pj=True)
    company_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="ID of the Company record created/updated (if PJ)",
    )
    professional_company_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="ID of the ProfessionalCompany link record (if PJ)",
    )

    # Link to version history (reuses ProfessionalVersion for payment data)
    payment_version_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="ID of the ProfessionalVersion created for payment data",
    )


class PaymentInfoStep(PaymentInfoStepBase, ScreeningStepMixin, table=True):
    """
    Payment info step table.

    Collects payment-related information:
    - Bank account details (bank, agency, account, PIX)
    - Company data if operating as PJ (CNPJ, razão social, etc.)

    Workflow:
    1. Professional indicates if operating as PF or PJ
    2. If PJ: fill company data (CNPJ, razão social, etc.)
    3. Fill bank account data (can be personal or company account)
    4. On submit: create ProfessionalVersion with payment snapshot
    5. Store version_id for audit trail
    """

    __tablename__ = "screening_payment_info_steps"
    __table_args__ = (
        UniqueConstraint(
            "process_id",
            name="uq_screening_payment_info_steps_process_id",
        ),
        Index("ix_screening_payment_info_steps_process_id", "process_id"),
        Index("ix_screening_payment_info_steps_status", "status"),
    )

    step_type: StepType = Field(
        default=StepType.PAYMENT_INFO,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=False),
    )

    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
    )

    # Foreign key to ProfessionalVersion (for payment data history)
    payment_version_id: Optional[UUID] = Field(
        default=None,
        foreign_key="professional_versions.id",
        nullable=True,
        description="Version snapshot created for payment data",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="payment_info_step")
    payment_version: Optional["ProfessionalVersion"] = Relationship()

    @property
    def has_bank_account(self) -> bool:
        """Check if a bank account record was created/linked."""
        return self.bank_account_id is not None

    @property
    def has_company(self) -> bool:
        """Check if company records were created/linked."""
        return self.company_id is not None and self.professional_company_id is not None

    @property
    def has_version(self) -> bool:
        """Check if a version snapshot was created."""
        return self.payment_version_id is not None

    @property
    def is_complete(self) -> bool:
        """Check if payment info is complete based on PJ status."""
        if self.is_pj:
            return self.has_bank_account and self.has_company
        return self.has_bank_account
