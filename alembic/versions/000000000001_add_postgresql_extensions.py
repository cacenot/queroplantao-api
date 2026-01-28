"""add_postgresql_extensions

Revision ID: 000000000001
Revises:
Create Date: 2026-01-27 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000000000001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create PostgreSQL extensions required by the application."""
    connection = op.get_bind()

    # pg_trgm - For trigram-based text search (GIN indexes)
    connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

    # unaccent - For accent-insensitive search
    connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS unaccent"))

    # Create immutable unaccent function for use in indexes
    connection.execute(
        sa.text("""
        CREATE OR REPLACE FUNCTION f_unaccent(text)
        RETURNS text AS
        $func$
        SELECT public.unaccent('public.unaccent', $1)
        $func$
        LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT;
    """)
    )


def downgrade() -> None:
    """Remove PostgreSQL extensions."""
    connection = op.get_bind()

    # Drop immutable unaccent function
    connection.execute(sa.text("DROP FUNCTION IF EXISTS f_unaccent(text)"))

    # Drop extensions
    connection.execute(sa.text("DROP EXTENSION IF EXISTS unaccent"))
    connection.execute(sa.text("DROP EXTENSION IF EXISTS pg_trgm"))
