"""add_screening_cancellation_support

Revision ID: 000000000005
Revises: 000000000004
Create Date: 2026-01-28 08:00:00.000000

This migration adds support for cancelling screening processes:
- Adds cancelled_at, cancelled_by, and cancellation_reason columns to screening_processes
- Adds CANCELLED value to step_status enum

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000005"
down_revision: Union[str, Sequence[str], None] = "000000000004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cancellation support to screening processes."""
    # Add CANCELLED value to step_status enum
    op.execute("ALTER TYPE step_status ADD VALUE IF NOT EXISTS 'CANCELLED'")

    # Add cancellation fields to screening_processes table
    op.add_column(
        "screening_processes",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "screening_processes",
        sa.Column("cancelled_by", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "screening_processes",
        sa.Column(
            "cancellation_reason",
            sqlmodel.sql.sqltypes.AutoString(length=2000),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove cancellation support from screening processes.

    Note: PostgreSQL does not support removing values from enums directly.
    The CANCELLED value will remain in the step_status enum.
    """
    op.drop_column("screening_processes", "cancellation_reason")
    op.drop_column("screening_processes", "cancelled_by")
    op.drop_column("screening_processes", "cancelled_at")
