"""Base repository with common CRUD operations."""

from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from src.app.exceptions import NotFoundError


if TYPE_CHECKING:
    from fastapi_restkit.filterset import FilterSet
    from fastapi_restkit.sortingset import SortingSet


ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    """
    Base repository for CRUD operations.

    Provides standard CRUD methods and paginated list functionality.
    Subclasses can override `get_query()` to customize the base query
    (e.g., to exclude soft-deleted records).

    Usage:
        class UserRepository(BaseRepository[User]):
            model = User
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_query(self) -> Select[tuple[ModelT]]:
        """
        Get the base query for this repository.

        Override this method in subclasses to customize the base query
        (e.g., to exclude soft-deleted records).

        Returns:
            Select query for the model.
        """
        return select(self.model)

    async def get_by_id(self, id: UUID) -> ModelT | None:
        """Get entity by ID."""
        query = self.get_query().where(self.model.id == id)  # type: ignore[attr-defined]
        result = await self.session.execute(query)
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
        *,
        filters: "FilterSet | None" = None,
        sorting: "SortingSet | None" = None,
        limit: int = 25,
        offset: int = 0,
        base_query: Select[tuple[ModelT]] | None = None,
    ) -> PaginatedResponse[ModelT]:
        """
        List entities with pagination, filtering, and sorting.

        Args:
            filters: Optional FilterSet to apply.
            sorting: Optional SortingSet to apply.
            limit: Maximum number of items to return (default: 25).
            offset: Number of items to skip (default: 0).
            base_query: Optional custom base query. If not provided, uses get_query().

        Returns:
            PaginatedResponse with items and pagination metadata.
        """
        # Build base query
        query = base_query if base_query is not None else self.get_query()

        # Apply filters using FilterSet.apply_to_query()
        if filters:
            query = filters.apply_to_query(query, self.model)

        # Apply sorting using SortingSet.apply_to_query()
        if sorting:
            query = sorting.apply_to_query(query, self.model)
        elif hasattr(self.model, "created_at"):
            query = query.order_by(desc(self.model.created_at))  # type: ignore[attr-defined]

        # Count total matching records (apply filters to count query too)
        count_base = base_query if base_query is not None else self.get_query()
        if filters:
            count_base = filters.apply_to_query(count_base, self.model)
        count_query = select(func.count()).select_from(count_base.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination and execute
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        page = (offset // limit) + 1 if limit > 0 else 1
        pagination = PaginationParams(page=page, page_size=limit)

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

    async def list_all(
        self,
        *,
        filters: "FilterSet | None" = None,
        sorting: "SortingSet | None" = None,
        base_query: Select[tuple[ModelT]] | None = None,
    ) -> list[ModelT]:
        """
        List all entities without pagination.

        Use this method for dropdown lists, caching scenarios,
        or when the dataset is known to be small.

        Args:
            filters: Optional FilterSet to apply.
            sorting: Optional SortingSet to apply.
            base_query: Optional custom base query. If not provided, uses get_query().

        Returns:
            List of all matching entities.
        """
        # Build base query
        query = base_query if base_query is not None else self.get_query()

        # Apply filters using FilterSet.apply_to_query()
        if filters:
            query = filters.apply_to_query(query, self.model)

        # Apply sorting using SortingSet.apply_to_query()
        if sorting:
            query = sorting.apply_to_query(query, self.model)
        elif hasattr(self.model, "created_at"):
            query = query.order_by(desc(self.model.created_at))  # type: ignore[attr-defined]

        result = await self.session.execute(query)
        return list(result.scalars().all())
