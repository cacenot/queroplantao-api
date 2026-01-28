import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, text
from sqlalchemy import pool

from alembic import context

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app.config import Settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load settings from .env and override URL
settings = Settings()
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

# Import models for autogenerate support
# Order matters! Import modules with dependencies after their dependents
# Use direct model imports to avoid loading presentation/routes that may have broken schemas

from src.modules.users.domain.models import *  # noqa: E402, F401, F403
from src.modules.professionals.domain.models import *  # noqa: E402, F401, F403
from src.modules.organizations.domain.models import *  # noqa: E402, F401, F403
from src.modules.units.domain.models import *  # noqa: E402, F401, F403
from src.modules.contracts.domain.models import *  # noqa: E402, F401, F403
from src.modules.screening.domain.models import *  # noqa: E402, F401, F403

# Import shared models AFTER contracts (BankAccount references ProfessionalContract)
from src.shared.domain.models import *  # noqa: E402, F401, F403

# Import SQLModel metadata
from sqlmodel import SQLModel  # noqa: E402

target_metadata = SQLModel.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create required extensions BEFORE transactional migrations
        # These need to be committed separately to be visible in the same session
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        connection.execute(
            text("""
            CREATE OR REPLACE FUNCTION f_unaccent(text)
            RETURNS text AS $$
            SELECT unaccent($1)
            $$ LANGUAGE SQL IMMUTABLE PARALLEL SAFE STRICT
        """)
        )
        connection.commit()

        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
