"""add_cpf_to_users

Revision ID: c724fe9c3d80
Revises: 6c70dbce726c
Create Date: 2026-01-20 16:51:35.877064

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "c724fe9c3d80"
down_revision: Union[str, Sequence[str], None] = "6c70dbce726c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add CPF column to users table
    op.add_column(
        "users",
        sa.Column("cpf", sqlmodel.sql.sqltypes.AutoString(length=11), nullable=True),
    )
    op.create_unique_constraint("uq_users_cpf", "users", ["cpf"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_users_cpf", "users", type_="unique")
    op.drop_column("users", "cpf")
