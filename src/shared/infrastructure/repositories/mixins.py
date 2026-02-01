"""Repository mixins for common functionality."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlmodel import SQLModel

from src.app.exceptions import NotFoundError


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


ModelT = TypeVar("ModelT", bound=SQLModel)


class SoftDeleteMixin(Generic[ModelT]):
    """
    Mixin that provides soft delete functionality for repositories.

    This mixin assumes the model has a `deleted_at` field (from SoftDeleteMixin model).
    It overrides `get_query()` to automatically exclude soft-deleted records
    and provides methods for soft delete operations.

    Usage:
        class ProfessionalRepository(SoftDeleteMixin[Professional], BaseRepository[Professional]):
            model = Professional

    Note:
        This mixin must be listed BEFORE BaseRepository in the inheritance chain
        to properly override `get_query()`.
    """

    model: type[ModelT]
    session: "AsyncSession"

    def get_query(self) -> Select[tuple[ModelT]]:
        """
        Get base query with soft-delete filter applied.

        Returns:
            Select query excluding soft-deleted records.
        """
        return select(self.model).where(self.model.deleted_at.is_(None))  # type: ignore[attr-defined]

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

    async def delete(self, id: UUID) -> None:
        """
        Soft delete an entity by setting deleted_at timestamp.

        Overrides BaseRepository.delete() to perform soft delete instead of hard delete.

        Args:
            id: The entity UUID to soft delete.

        Raises:
            NotFoundError: If entity not found or already soft-deleted.
        """
        entity = await self.get_by_id_or_raise(id)  # type: ignore[attr-defined]
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
