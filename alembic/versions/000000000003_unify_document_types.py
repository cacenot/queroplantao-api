"""Unify document types into shared module.

This migration:
1. Creates the new document_types table in shared module
2. Migrates professional_documents to use document_type_id FK
3. Migrates screening_documents to use document_type_id FK
4. Drops the old document_type_configs table

Revision ID: 000000000003
Revises: 000000000002
Create Date: 2026-01-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "000000000003"
down_revision: Union[str, Sequence[str], None] = "000000000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create document_types table and migrate existing data."""

    # Create the DocumentCategory enum if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documentcategory') THEN
                CREATE TYPE documentcategory AS ENUM ('PROFILE', 'QUALIFICATION', 'SPECIALTY');
            END IF;
        END$$;
    """)

    # 1. Create new document_types table
    op.create_table(
        "document_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "category",
            postgresql.ENUM(
                "PROFILE",
                "QUALIFICATION",
                "SPECIALTY",
                name="documentcategory",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("help_text", sa.String(length=1000), nullable=True),
        sa.Column("validation_instructions", sa.Text(), nullable=True),
        sa.Column("validation_url", sa.String(length=500), nullable=True),
        sa.Column(
            "requires_expiration", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("default_validity_days", sa.Integer(), nullable=True),
        sa.Column("required_for_professional_types", postgresql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("organization_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_document_types_category", "document_types", ["category"])
    op.create_index("ix_document_types_is_active", "document_types", ["is_active"])
    op.create_index(
        "ix_document_types_organization_id", "document_types", ["organization_id"]
    )
    op.create_index(
        "ix_document_types_code_global_active",
        "document_types",
        ["code"],
        unique=True,
        postgresql_where=sa.text("organization_id IS NULL AND deleted_at IS NULL"),
    )

    # 2. Update professional_documents table
    # Add new column
    op.add_column(
        "professional_documents",
        sa.Column("document_type_id", sa.UUID(), nullable=True),
    )

    # We can't migrate data yet because document_types is empty
    # The seed migration (000000000004) will populate it, then we need to update FKs

    # 3. Update screening_documents table
    # Drop old FK constraint first
    op.execute("""
        ALTER TABLE screening_documents
        DROP CONSTRAINT IF EXISTS screening_documents_document_type_config_id_fkey;
    """)

    # Add new column
    op.add_column(
        "screening_documents",
        sa.Column("document_type_id", sa.UUID(), nullable=True),
    )

    # Drop old column if exists
    op.execute("""
        ALTER TABLE screening_documents
        DROP COLUMN IF EXISTS document_type_config_id;
    """)

    # Drop old category column if exists
    op.execute("""
        ALTER TABLE screening_documents
        DROP COLUMN IF EXISTS document_category;
    """)

    # 4. Drop old table document_type_configs
    op.execute("DROP TABLE IF EXISTS document_type_configs CASCADE;")

    # 5. Update professional_documents - drop old columns
    op.execute("""
        ALTER TABLE professional_documents
        DROP COLUMN IF EXISTS document_type;
    """)
    op.execute("""
        ALTER TABLE professional_documents
        DROP COLUMN IF EXISTS document_category;
    """)

    # Drop old indexes if they exist
    op.execute("DROP INDEX IF EXISTS idx_professional_documents_category;")
    op.execute("DROP INDEX IF EXISTS idx_professional_documents_type;")
    op.execute("DROP INDEX IF EXISTS ix_screening_documents_category;")
    op.execute("DROP INDEX IF EXISTS ix_document_type_configs_category;")
    op.execute("DROP INDEX IF EXISTS ix_document_type_configs_code_active;")
    op.execute("DROP INDEX IF EXISTS ix_document_type_configs_is_active;")

    # Create new indexes
    op.create_index(
        "idx_professional_documents_type_id",
        "professional_documents",
        ["document_type_id"],
    )
    op.create_index(
        "ix_screening_documents_document_type_id",
        "screening_documents",
        ["document_type_id"],
    )

    # Drop old unique constraint
    op.execute("""
        ALTER TABLE screening_documents
        DROP CONSTRAINT IF EXISTS uq_screening_documents_step_doc_config;
    """)

    # Note: FK constraints will be added after seed data is populated
    # This is handled in a separate step or manually


def downgrade() -> None:
    """Revert to previous schema."""
    # This is a destructive migration - downgrade would require data restoration
    # For development, we can just drop the new table and recreate old structure

    # Drop new indexes
    op.execute("DROP INDEX IF EXISTS idx_professional_documents_type_id;")
    op.execute("DROP INDEX IF EXISTS ix_screening_documents_document_type_id;")
    op.execute("DROP INDEX IF EXISTS ix_document_types_code_global_active;")
    op.execute("DROP INDEX IF EXISTS ix_document_types_organization_id;")
    op.execute("DROP INDEX IF EXISTS ix_document_types_is_active;")
    op.execute("DROP INDEX IF EXISTS ix_document_types_category;")

    # Drop new columns
    op.drop_column("professional_documents", "document_type_id")
    op.drop_column("screening_documents", "document_type_id")

    # Drop new table
    op.drop_table("document_types")

    # Recreate old enum columns would require re-adding them
    # This is simplified for development purposes
