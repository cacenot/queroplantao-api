"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies.settings import get_settings


def create_engine():
    """Create async database engine."""
    settings = get_settings()

    engine = create_async_engine(
        settings.database_url_async,
        **settings.neon_connection_args_async,
        pool_pre_ping=True,
    )

    return engine


# Global engine instance
engine = create_engine()

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
