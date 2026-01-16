"""Database session dependency for FastAPI injection."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database.connection import async_session_factory


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Dependency to get async database session.

    Usage:
        @router.get("/items")
        async def get_items(session: SessionDep):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]
