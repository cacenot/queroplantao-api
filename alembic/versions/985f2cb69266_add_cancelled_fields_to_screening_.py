"""add_cancelled_fields_to_screening_process

Revision ID: 985f2cb69266
Revises: 000000000004
Create Date: 2026-01-28 07:49:23.018383

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "985f2cb69266"
down_revision: Union[str, Sequence[str], None] = "000000000004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cancelled_at, cancelled_by, and cancellation_reason columns to screening_processes."""
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
    """Remove cancelled_at, cancelled_by, and cancellation_reason columns from screening_processes."""
    op.drop_column("screening_processes", "cancellation_reason")
    op.drop_column("screening_processes", "cancelled_by")
    op.drop_column("screening_processes", "cancelled_at")
