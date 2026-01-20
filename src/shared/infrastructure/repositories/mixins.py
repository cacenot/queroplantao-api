"""Repository mixins for common functionality."""

from typing import Generic, TypeVar

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel


ModelT = TypeVar("ModelT", bound=SQLModel)


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
