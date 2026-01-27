"""remove_interview_from_screening

Revision ID: 4ab2c4a709ae
Revises: fb5c91a3e7d8
Create Date: 2026-01-26 09:39:41.327974

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4ab2c4a709ae"
down_revision: Union[str, Sequence[str], None] = "fb5c91a3e7d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove interview fields from organization_screening_settings
    op.drop_column("organization_screening_settings", "requires_interview")
    op.drop_column("organization_screening_settings", "default_interview_method")

    # Remove interview fields from screening_process_steps
    op.drop_column("screening_process_steps", "interview_method")
    op.drop_column("screening_process_steps", "interview_notes")
    op.drop_column("screening_process_steps", "interview_outcome")
    op.drop_column("screening_process_steps", "interview_date")
    op.drop_column("screening_process_steps", "interview_escalation_reason")


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add interview fields to screening_process_steps
    op.add_column(
        "screening_process_steps",
        sa.Column(
            "interview_escalation_reason",
            sa.VARCHAR(length=2000),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "screening_process_steps",
        sa.Column(
            "interview_date",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "screening_process_steps",
        sa.Column(
            "interview_outcome",
            postgresql.ENUM(
                "APPROVED",
                "REJECTED",
                "ESCALATED",
                "RESCHEDULED",
                name="interview_outcome",
            ),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "screening_process_steps",
        sa.Column(
            "interview_notes",
            sa.VARCHAR(length=4000),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "screening_process_steps",
        sa.Column(
            "interview_method",
            postgresql.ENUM(
                "PHONE_CALL",
                "VIDEO_CALL",
                "IN_PERSON",
                "WHATSAPP",
                name="interview_method",
            ),
            autoincrement=False,
            nullable=True,
        ),
    )

    # Re-add interview fields to organization_screening_settings
    op.add_column(
        "organization_screening_settings",
        sa.Column(
            "default_interview_method",
            sa.VARCHAR(length=50),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "organization_screening_settings",
        sa.Column(
            "requires_interview", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
    )
