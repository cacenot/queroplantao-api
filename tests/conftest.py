"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.app.context import RequestContext, set_request_context
from src.shared.infrastructure.database.connection import async_session_factory

from uuid import UUID


@pytest.fixture
async def test_db_session() -> AsyncSession:
    """Create test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_session_factory(bind=engine)

    session: AsyncSession
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def test_context() -> RequestContext:
    """Create test request context."""
    context = RequestContext(
        user_id=UUID("12345678-1234-5678-1234-567812345678"),
        tenant_id=UUID("87654321-4321-8765-4321-876543218765"),
        roles=["admin"],
    )
    set_request_context(context)
    return context


@pytest.fixture
def test_context_user() -> UUID:
    """Get test user ID."""
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def test_context_tenant() -> UUID:
    """Get test tenant ID."""
    return UUID("87654321-4321-8765-4321-876543218765")
