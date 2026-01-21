"""add search indexes and extensions

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-21 11:00:00.000000

This migration:
1. Enables PostgreSQL extensions for fuzzy text search:
   - pg_trgm: Trigram-based similarity search
   - unaccent: Accent-insensitive search
2. Creates immutable f_unaccent function for use in indexes

Note: The actual indexes are defined in the SQLModel models and will be
created by subsequent Alembic auto-generated migrations.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # =========================================================================
    # 1. ENABLE POSTGRESQL EXTENSIONS
    # =========================================================================

    # Enable pg_trgm for trigram-based fuzzy text search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Enable unaccent for accent-insensitive search
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")

    # =========================================================================
    # 2. CREATE IMMUTABLE UNACCENT FUNCTION FOR USE IN INDEXES
    # =========================================================================

    # Create immutable wrapper for unaccent (required for indexes)
    # PostgreSQL requires IMMUTABLE functions for index expressions
    op.execute("""
        CREATE OR REPLACE FUNCTION f_unaccent(text)
        RETURNS text AS $$
            SELECT public.unaccent('public.unaccent', $1)
        $$ LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the immutable unaccent function
    op.execute("DROP FUNCTION IF EXISTS f_unaccent(text)")

    # Note: Not dropping extensions as they might be used elsewhere
    # op.execute("DROP EXTENSION IF EXISTS unaccent")
    # op.execute("DROP EXTENSION IF EXISTS pg_trgm")
