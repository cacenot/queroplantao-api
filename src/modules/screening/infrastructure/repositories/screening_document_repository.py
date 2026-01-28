"""ScreeningDocument repository for database operations."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.screening.domain.models import (
    ScreeningDocument,
    ScreeningDocumentStatus,
)
from src.shared.infrastructure.repositories import BaseRepository


class ScreeningDocumentRepository(BaseRepository[ScreeningDocument]):
    """
    Repository for ScreeningDocument model.

    Provides operations for managing screening documents within an upload step.
    Documents are tied to the step lifecycle (no soft delete).
    """

    model = ScreeningDocument

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_step(
        self,
        upload_step_id: UUID,
    ) -> Select[tuple[ScreeningDocument]]:
        """
        Get base query filtered by upload step.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            Query filtered by upload step.
        """
        return select(ScreeningDocument).where(
            ScreeningDocument.upload_step_id == upload_step_id
        )

    async def get_by_id_for_step(
        self,
        id: UUID,
        upload_step_id: UUID,
    ) -> ScreeningDocument | None:
        """
        Get document by ID for a specific upload step.

        Args:
            id: The screening document UUID.
            upload_step_id: The document upload step UUID.

        Returns:
            ScreeningDocument if found, None otherwise.
        """
        query = self._base_query_for_step(upload_step_id).where(
            ScreeningDocument.id == id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_type(
        self,
        id: UUID,
    ) -> ScreeningDocument | None:
        """
        Get document by ID with document type loaded.

        Args:
            id: The screening document UUID.

        Returns:
            ScreeningDocument with document_type loaded, or None.
        """
        query = (
            select(ScreeningDocument)
            .where(ScreeningDocument.id == id)
            .options(selectinload(ScreeningDocument.document_type))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_step(
        self,
        upload_step_id: UUID,
    ) -> list[ScreeningDocument]:
        """
        List all documents for an upload step, ordered by display order.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            List of screening documents ordered by order field.
        """
        query = self._base_query_for_step(upload_step_id).order_by(
            ScreeningDocument.order
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_for_step_with_types(
        self,
        upload_step_id: UUID,
    ) -> list[ScreeningDocument]:
        """
        List documents with document types loaded.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            List of documents with document_type relationship loaded.
        """
        query = (
            self._base_query_for_step(upload_step_id)
            .options(selectinload(ScreeningDocument.document_type))
            .order_by(ScreeningDocument.order)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_pending_uploads(
        self,
        upload_step_id: UUID,
    ) -> list[ScreeningDocument]:
        """
        Get documents that need to be uploaded.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            List of documents with status PENDING_UPLOAD.
        """
        query = self._base_query_for_step(upload_step_id).where(
            ScreeningDocument.status == ScreeningDocumentStatus.PENDING_UPLOAD
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_pending_review(
        self,
        upload_step_id: UUID,
    ) -> list[ScreeningDocument]:
        """
        Get documents that are waiting for review.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            List of documents with status PENDING_REVIEW.
        """
        query = self._base_query_for_step(upload_step_id).where(
            ScreeningDocument.status == ScreeningDocumentStatus.PENDING_REVIEW
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_required_pending(
        self,
        upload_step_id: UUID,
    ) -> list[ScreeningDocument]:
        """
        Get required documents that still need action (upload or rejected).

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            List of required documents not yet satisfied.
        """
        pending_statuses = [
            ScreeningDocumentStatus.PENDING_UPLOAD,
            ScreeningDocumentStatus.REJECTED,
        ]
        query = (
            self._base_query_for_step(upload_step_id)
            .where(ScreeningDocument.is_required.is_(True))
            .where(ScreeningDocument.status.in_(pending_statuses))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_with_alerts(
        self,
        upload_step_id: UUID,
    ) -> list[ScreeningDocument]:
        """
        Get documents with ALERT status that need supervisor review.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            List of documents with status ALERT.
        """
        query = self._base_query_for_step(upload_step_id).where(
            ScreeningDocument.status == ScreeningDocumentStatus.ALERT
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_document_type(
        self,
        upload_step_id: UUID,
        document_type_id: UUID,
    ) -> ScreeningDocument | None:
        """
        Get document by type for an upload step.

        Args:
            upload_step_id: The document upload step UUID.
            document_type_id: The document type UUID.

        Returns:
            ScreeningDocument if found, None otherwise.
        """
        query = self._base_query_for_step(upload_step_id).where(
            ScreeningDocument.document_type_id == document_type_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_status(
        self,
        upload_step_id: UUID,
    ) -> dict[ScreeningDocumentStatus, int]:
        """
        Count documents by status for an upload step.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            Dict mapping status to count.
        """
        from sqlalchemy import func

        query = (
            select(
                ScreeningDocument.status,
                func.count(ScreeningDocument.id).label("count"),
            )
            .where(ScreeningDocument.upload_step_id == upload_step_id)
            .group_by(ScreeningDocument.status)
        )
        result = await self.session.execute(query)
        rows = result.all()
        return {row.status: row.count for row in rows}

    async def are_all_approved(
        self,
        upload_step_id: UUID,
    ) -> bool:
        """
        Check if all required documents are approved.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            True if all required documents are approved.
        """
        approved_statuses = [
            ScreeningDocumentStatus.APPROVED,
            ScreeningDocumentStatus.REUSED,
        ]
        # Check if there are any required documents not in approved states
        query = (
            select(ScreeningDocument.id)
            .where(ScreeningDocument.upload_step_id == upload_step_id)
            .where(ScreeningDocument.is_required.is_(True))
            .where(ScreeningDocument.status.not_in(approved_statuses))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is None

    async def has_alerts(
        self,
        upload_step_id: UUID,
    ) -> bool:
        """
        Check if any document has ALERT status.

        Args:
            upload_step_id: The document upload step UUID.

        Returns:
            True if any document has ALERT status.
        """
        query = (
            select(ScreeningDocument.id)
            .where(ScreeningDocument.upload_step_id == upload_step_id)
            .where(ScreeningDocument.status == ScreeningDocumentStatus.ALERT)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def bulk_create(
        self,
        documents: list[ScreeningDocument],
    ) -> list[ScreeningDocument]:
        """
        Bulk create screening documents.

        Args:
            documents: List of ScreeningDocument instances to create.

        Returns:
            List of created documents.
        """
        for doc in documents:
            self.session.add(doc)
        await self.session.flush()
        return documents
