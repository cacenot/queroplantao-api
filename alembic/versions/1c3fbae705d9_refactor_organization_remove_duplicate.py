"""refactor organization remove duplicate

Revision ID: 1c3fbae705d9
Revises: 9fd32650c669
Create Date: 2026-01-21 21:04:59.760178

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1c3fbae705d9"
down_revision: Union[str, Sequence[str], None] = "9fd32650c669"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make company_id required
    op.alter_column(
        "organizations", "company_id", existing_type=sa.UUID(), nullable=False
    )

    # Drop unique constraint on cnpj (data moves to company)
    op.drop_index(
        "uq_organizations_cnpj",
        table_name="organizations",
    )

    # Drop FK for verified_by
    op.drop_constraint(
        "organizations_verified_by_fkey", "organizations", type_="foreignkey"
    )

    # Drop duplicate columns (data is in Company now)
    op.drop_column("organizations", "verified_by")
    op.drop_column("organizations", "verified_at")
    op.drop_column("organizations", "cnpj")
    op.drop_column("organizations", "trading_name")
    op.drop_column("organizations", "email")
    op.drop_column("organizations", "phone")
    op.drop_column("organizations", "website")
    op.drop_column("organizations", "address")
    op.drop_column("organizations", "number")
    op.drop_column("organizations", "complement")
    op.drop_column("organizations", "neighborhood")
    op.drop_column("organizations", "city")
    op.drop_column("organizations", "state_code")
    op.drop_column("organizations", "state_name")
    op.drop_column("organizations", "postal_code")
    op.drop_column("organizations", "latitude")
    op.drop_column("organizations", "longitude")


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add columns
    op.add_column(
        "organizations",
        sa.Column("longitude", sa.DOUBLE_PRECISION(), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("latitude", sa.DOUBLE_PRECISION(), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("state_name", sa.VARCHAR(length=100), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("state_code", sa.VARCHAR(length=2), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("postal_code", sa.VARCHAR(length=10), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("city", sa.VARCHAR(length=100), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("neighborhood", sa.VARCHAR(length=100), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("complement", sa.VARCHAR(length=100), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("number", sa.VARCHAR(length=20), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("address", sa.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("website", sa.VARCHAR(length=500), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("phone", sa.VARCHAR(length=20), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("email", sa.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("trading_name", sa.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("cnpj", sa.VARCHAR(length=14), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("verified_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("verified_by", sa.UUID(), nullable=True),
    )

    # Recreate FK for verified_by
    op.create_foreign_key(
        "organizations_verified_by_fkey",
        "organizations",
        "users",
        ["verified_by"],
        ["id"],
    )

    # Recreate unique constraint on cnpj
    op.create_index(
        "uq_organizations_cnpj",
        "organizations",
        ["cnpj"],
        unique=True,
        postgresql_where=sa.text("cnpj IS NOT NULL AND deleted_at IS NULL"),
    )

    # Make company_id nullable again
    op.alter_column(
        "organizations", "company_id", existing_type=sa.UUID(), nullable=True
    )
