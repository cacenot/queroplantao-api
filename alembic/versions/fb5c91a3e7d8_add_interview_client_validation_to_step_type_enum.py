"""Add INTERVIEW and CLIENT_VALIDATION to step_type enum.

Revision ID: fb5c91a3e7d8
Revises: a1b2c3d4e5f7
Create Date: 2024-01-15 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "fb5c91a3e7d8"
down_revision: Union[str, None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add INTERVIEW and CLIENT_VALIDATION to step_type enum."""
    # PostgreSQL requires direct SQL to add values to an existing enum
    op.execute("ALTER TYPE step_type ADD VALUE IF NOT EXISTS 'INTERVIEW'")
    op.execute("ALTER TYPE step_type ADD VALUE IF NOT EXISTS 'CLIENT_VALIDATION'")


def downgrade() -> None:
    """Remove INTERVIEW and CLIENT_VALIDATION from step_type enum.

    Note: PostgreSQL doesn't support removing values from an enum directly.
    This would require recreating the enum type, which is complex.
    For safety, we don't remove the values - they can remain unused.
    """
    pass
