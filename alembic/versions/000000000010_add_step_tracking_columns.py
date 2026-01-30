"""Add step tracking columns to screening_processes.

Revision ID: 000000000010
Revises: 000000000009
Create Date: 2026-01-29 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "000000000010"
down_revision: str | Sequence[str] | None = "000000000009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add current_step_type column (required, default to CONVERSATION)
    op.add_column(
        "screening_processes",
        sa.Column(
            "current_step_type",
            sa.Enum(
                "CONVERSATION",
                "PROFESSIONAL_DATA",
                "DOCUMENT_UPLOAD",
                "DOCUMENT_REVIEW",
                "PAYMENT_INFO",
                "CLIENT_VALIDATION",
                name="step_type",
                create_constraint=False,
            ),
            nullable=False,
            server_default="CONVERSATION",
        ),
    )

    # Add configured_step_types as array of strings
    op.add_column(
        "screening_processes",
        sa.Column(
            "configured_step_types",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
    )

    # Add index for filtering by current step type
    op.create_index(
        "ix_screening_processes_current_step_type",
        "screening_processes",
        ["current_step_type"],
    )

    # Remove DRAFT from screening_status enum
    # First, update any existing DRAFT records to IN_PROGRESS
    op.execute(
        "UPDATE screening_processes SET status = 'IN_PROGRESS' WHERE status = 'DRAFT'"
    )

    # Rename old enum, create new one without DRAFT, update column, drop old enum
    op.execute("ALTER TYPE screening_status RENAME TO screening_status_old")
    op.execute(
        "CREATE TYPE screening_status AS ENUM ("
        "'IN_PROGRESS', 'PENDING_SUPERVISOR', 'APPROVED', 'REJECTED', 'EXPIRED', 'CANCELLED'"
        ")"
    )
    op.execute(
        "ALTER TABLE screening_processes "
        "ALTER COLUMN status TYPE screening_status "
        "USING status::text::screening_status"
    )
    op.execute("DROP TYPE screening_status_old")


def downgrade() -> None:
    # Restore DRAFT to screening_status enum
    op.execute("ALTER TYPE screening_status RENAME TO screening_status_old")
    op.execute(
        "CREATE TYPE screening_status AS ENUM ("
        "'DRAFT', 'IN_PROGRESS', 'PENDING_SUPERVISOR', 'APPROVED', 'REJECTED', 'EXPIRED', 'CANCELLED'"
        ")"
    )
    op.execute(
        "ALTER TABLE screening_processes "
        "ALTER COLUMN status TYPE screening_status "
        "USING status::text::screening_status"
    )
    op.execute("DROP TYPE screening_status_old")

    # Drop index
    op.drop_index("ix_screening_processes_current_step_type", "screening_processes")

    # Drop columns
    op.drop_column("screening_processes", "configured_step_types")
    op.drop_column("screening_processes", "current_step_type")
