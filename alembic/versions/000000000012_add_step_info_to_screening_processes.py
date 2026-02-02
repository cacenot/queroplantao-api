"""add_step_info_to_screening_processes

Revision ID: 000000000012
Revises: 000000000011
Create Date: 2026-02-02 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "000000000012"
down_revision: Union[str, Sequence[str], None] = "000000000011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "screening_processes",
        sa.Column(
            "step_info",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("screening_processes", "step_info")
