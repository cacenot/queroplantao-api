"""ScreeningRequiredDocument repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.screening.domain.models import ScreeningRequiredDocument
from src.modules.screening.domain.models.enums import RequiredDocumentStatus
from src.shared.infrastructure.repositories import BaseRepository


class ScreeningRequiredDocumentRepository(BaseRepository[ScreeningRequiredDocument]):
    """
    Repository for ScreeningRequiredDocument model.

    Provides operations for managing required documents within a screening process.
    """

    model = ScreeningRequiredDocument

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_process(
        self,
        process_id: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """
        List all required documents for a process.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of required documents.
        """
        query = select(self.model).where(self.model.process_id == process_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_process_with_reviews(
        self,
        process_id: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """
        List required documents with their reviews loaded.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of required documents with reviews.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .options(
                selectinload(self.model.reviews),
                selectinload(self.model.document_type_config),
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_uploads(
        self,
        process_id: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """
        Get required documents that haven't been uploaded yet.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of documents with is_uploaded=False.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.is_uploaded == False)  # noqa: E712
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_required_pending_uploads(
        self,
        process_id: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """
        Get REQUIRED documents that haven't been uploaded yet.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of required documents with is_uploaded=False.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.is_required == True)  # noqa: E712
            .where(self.model.is_uploaded == False)  # noqa: E712
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def bulk_create(
        self,
        documents: list[ScreeningRequiredDocument],
    ) -> list[ScreeningRequiredDocument]:
        """
        Create multiple required documents at once.

        Args:
            documents: List of documents to create.

        Returns:
            List of created documents.
        """
        self.session.add_all(documents)
        await self.session.flush()
        for doc in documents:
            await self.session.refresh(doc)
        return documents

    async def delete_by_process(
        self,
        process_id: UUID,
    ) -> int:
        """
        Delete all required documents for a process.

        Used when recreating document selection.

        Args:
            process_id: The screening process UUID.

        Returns:
            Number of deleted documents.
        """
        from sqlalchemy import delete

        stmt = delete(self.model).where(self.model.process_id == process_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def list_by_status(
        self,
        process_id: UUID,
        status: RequiredDocumentStatus,
    ) -> list[ScreeningRequiredDocument]:
        """
        List documents with a specific status.

        Args:
            process_id: The screening process UUID.
            status: The status to filter by.

        Returns:
            List of documents with the specified status.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == status)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_required_not_uploaded(
        self,
        process_id: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """
        Get required documents that are still pending upload.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of required documents with status = PENDING_UPLOAD.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.is_required == True)  # noqa: E712
            .where(self.model.status == RequiredDocumentStatus.PENDING_UPLOAD)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_pending_review(
        self,
        process_id: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """
        Get documents that are waiting for review (status = UPLOADED).

        Args:
            process_id: The screening process UUID.

        Returns:
            List of documents with status = UPLOADED.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == RequiredDocumentStatus.UPLOADED)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_rejected(
        self,
        process_id: UUID,
    ) -> list[ScreeningRequiredDocument]:
        """
        Get documents that were rejected.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of documents with status = REJECTED.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == RequiredDocumentStatus.REJECTED)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
