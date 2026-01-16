"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from src.app.exceptions import NotFoundError
from src.shared.domain.schemas.common import PaginatedResponse, PaginationParams


ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    """
    Base repository for CRUD operations.
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
        # Count total
        count_query = select(func.count()).select_from(self.model)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Get items
        query = select(self.model).offset(pagination.offset).limit(pagination.limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return PaginatedResponse.create(
            items=items,
            total=total,
            pagination=pagination,
        )

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
