"""Repository mixins for common functionality."""

from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID

from fastapi_restkit.filterset import FilterSet
from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import SortingSet
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from src.app.exceptions import NotFoundError


ModelT = TypeVar("ModelT", bound=SQLModel)
FilterT = TypeVar("FilterT", bound=FilterSet)
SortingT = TypeVar("SortingT", bound=SortingSet)


class PaginationMixin(Generic[ModelT]):
    """
    Mixin that provides pagination functionality for repositories.

    This mixin uses fastapi-restkit's PaginationParams and PaginatedResponse
    to provide standardized pagination across all repositories.

    Usage:
        class UserRepository(PaginationMixin[User], BaseRepository[User]):
            model = User
    """

    model: type[ModelT]
    session: AsyncSession

    async def paginate(
        self,
        pagination: PaginationParams,
        query: Select[tuple[ModelT]] | None = None,
    ) -> PaginatedResponse[ModelT]:
        """
        Paginate query results.

        Args:
            pagination: Pagination parameters (page, page_size)
            query: Optional custom query. If not provided, selects all from model.

        Returns:
            PaginatedResponse with items and pagination metadata
        """
        if query is None:
            query = select(self.model)

        # Count total items
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        paginated_query = query.offset(pagination.offset).limit(pagination.limit)
        result = await self.session.execute(paginated_query)
        items = list(result.scalars().all())

        return PaginatedResponse.create(
            items=items,
            total=total,
            pagination=pagination,
        )


class SoftDeleteMixin(Generic[ModelT]):
    """
    Mixin that provides soft delete functionality for repositories.

    This mixin assumes the model has a `deleted_at` field (from SoftDeleteMixin model).
    It provides methods to:
    - Filter out soft-deleted records by default
    - Soft delete records instead of hard delete
    - Restore soft-deleted records

    Usage:
        class ProfessionalRepository(SoftDeleteMixin[Professional], BaseRepository[Professional]):
            model = Professional
    """

    model: type[ModelT]
    session: AsyncSession

    def _exclude_deleted(
        self,
        query: Select[tuple[ModelT]] | None = None,
    ) -> Select[tuple[ModelT]]:
        """
        Add a filter to exclude soft-deleted records.

        Args:
            query: Optional query to filter. If not provided, creates a new select.

        Returns:
            Query with deleted_at IS NULL filter applied.
        """
        if query is None:
            query = select(self.model)

        return query.where(self.model.deleted_at.is_(None))  # type: ignore[attr-defined]

    def _base_query(self) -> Select[tuple[ModelT]]:
        """
        Get base query with soft-delete filter applied.

        Returns:
            Select query excluding soft-deleted records.
        """
        return self._exclude_deleted()

    async def get_by_id(self, id: UUID) -> ModelT | None:
        """
        Get entity by ID, excluding soft-deleted records.

        Args:
            id: The entity UUID.

        Returns:
            The entity if found and not soft-deleted, None otherwise.
        """
        result = await self.session.execute(
            self._exclude_deleted().where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, id: UUID) -> ModelT:
        """
        Get entity by ID or raise NotFoundError.

        Args:
            id: The entity UUID.

        Returns:
            The entity if found and not soft-deleted.

        Raises:
            NotFoundError: If entity not found or is soft-deleted.
        """
        entity = await self.get_by_id(id)
        if entity is None:
            raise NotFoundError(
                resource=self.model.__name__,
                identifier=str(id),
            )
        return entity

    async def get_by_id_including_deleted(self, id: UUID) -> ModelT | None:
        """
        Get entity by ID including soft-deleted records.

        Useful for restore operations or auditing.

        Args:
            id: The entity UUID.

        Returns:
            The entity if found (including soft-deleted), None otherwise.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def soft_delete(self, id: UUID) -> None:
        """
        Soft delete an entity by setting deleted_at timestamp.

        Args:
            id: The entity UUID to soft delete.

        Raises:
            NotFoundError: If entity not found or already soft-deleted.
        """
        entity = await self.get_by_id_or_raise(id)
        entity.deleted_at = datetime.now(timezone.utc)  # type: ignore[attr-defined]
        self.session.add(entity)
        await self.session.flush()

    async def restore(self, id: UUID) -> ModelT:
        """
        Restore a soft-deleted entity by clearing deleted_at.

        Args:
            id: The entity UUID to restore.

        Returns:
            The restored entity.

        Raises:
            NotFoundError: If entity not found.
        """
        entity = await self.get_by_id_including_deleted(id)
        if entity is None:
            raise NotFoundError(
                resource=self.model.__name__,
                identifier=str(id),
            )
        entity.deleted_at = None  # type: ignore[attr-defined]
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def list(
        self,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ModelT]:
        """
        List entities with pagination, excluding soft-deleted.

        Args:
            pagination: Pagination parameters.

        Returns:
            PaginatedResponse with non-deleted items.
        """
        query = self._exclude_deleted()
        return await self.paginate(pagination, query)  # type: ignore[attr-defined]

    async def paginate(
        self,
        pagination: PaginationParams,
        query: Select[tuple[ModelT]] | None = None,
        *,
        filters: FilterSet | None = None,
        sorting: SortingSet | None = None,
    ) -> PaginatedResponse[ModelT]:
        """
        Paginate query results.

        Note: This method does NOT automatically exclude deleted records.
        Use _exclude_deleted() explicitly if needed.

        Args:
            pagination: Pagination parameters.
            query: Optional custom query.
            filters: Optional FilterSet to apply.
            sorting: Optional SortingSet to apply.

        Returns:
            PaginatedResponse with items and pagination metadata.
        """
        if query is None:
            query = select(self.model)

        # Apply filters if provided
        if filters:
            query = filters.apply_to_query(query, self.model)

        # Apply sorting if provided (otherwise use default id ordering for UUID v7)
        if sorting:
            query = sorting.apply_to_query(query, self.model)
        else:
            # Default sort by id (UUID v7 is time-ordered)
            query = query.order_by(self.model.id)  # type: ignore[attr-defined]

        # Count total items (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        paginated_query = query.offset(pagination.offset).limit(pagination.limit)
        result = await self.session.execute(paginated_query)
        items = list(result.scalars().all())

        return PaginatedResponse.create(
            items=items,
            total=total,
            pagination=pagination,
        )


class SoftDeletePaginationMixin(SoftDeleteMixin[ModelT], PaginationMixin[ModelT]):
    """
    Combined mixin that provides both soft delete and pagination functionality.

    This is the recommended mixin for repositories that need:
    - Soft delete (via deleted_at column)
    - Pagination with fastapi-restkit
    - Filtering with FilterSet
    - Sorting with SortingSet

    Usage:
        class ProfessionalRepository(
            SoftDeletePaginationMixin[Professional],
            BaseRepository[Professional]
        ):
            model = Professional
    """

    async def list_paginated(
        self,
        pagination: PaginationParams,
        *,
        filters: FilterSet | None = None,
        sorting: SortingSet | None = None,
        base_query: Select[tuple[ModelT]] | None = None,
    ) -> PaginatedResponse[ModelT]:
        """
        List entities with pagination, filtering, and sorting.

        Automatically excludes soft-deleted records.

        Args:
            pagination: Pagination parameters.
            filters: Optional FilterSet to apply.
            sorting: Optional SortingSet to apply.
            base_query: Optional base query (already filtered by tenant, etc.).

        Returns:
            PaginatedResponse with filtered, sorted, and paginated items.
        """
        # Start with base query or default (excluding deleted)
        if base_query is None:
            query = self._base_query()
        else:
            query = self._exclude_deleted(base_query)

        return await self.paginate(
            pagination,
            query,
            filters=filters,
            sorting=sorting,
        )
