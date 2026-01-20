"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar
from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from src.app.exceptions import NotFoundError
from src.shared.infrastructure.repositories.mixins import PaginationMixin


ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(PaginationMixin[ModelT], Generic[ModelT]):
    """
    Base repository for CRUD operations.

    Includes PaginationMixin for paginated queries using fastapi-restkit.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelT | None:
        """Get entity by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, id: UUID) -> ModelT:
        """Get entity by ID or raise NotFoundError."""
        entity = await self.get_by_id(id)
        if entity is None:
            raise NotFoundError(
                resource=self.model.__name__,
                identifier=str(id),
            )
        return entity

    async def list(
        self,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ModelT]:
        """List entities with pagination."""
        return await self.paginate(pagination)

    async def create(self, entity: ModelT) -> ModelT:
        """Create new entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        """Update existing entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: UUID) -> None:
        """Delete entity by ID."""
        entity = await self.get_by_id_or_raise(id)
        await self.session.delete(entity)
        await self.session.flush()
