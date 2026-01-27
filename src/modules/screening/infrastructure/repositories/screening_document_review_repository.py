"""ScreeningDocumentReview repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models import (
    DocumentReviewStatus,
    ScreeningDocumentReview,
)
from src.shared.infrastructure.repositories import BaseRepository


class ScreeningDocumentReviewRepository(BaseRepository[ScreeningDocumentReview]):
    """
    Repository for ScreeningDocumentReview model.

    Provides operations for managing document reviews within a screening process.
    """

    model = ScreeningDocumentReview

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_process(
        self,
        process_id: UUID,
    ) -> list[ScreeningDocumentReview]:
        """
        List all document reviews for a process.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of document reviews.
        """
        query = select(self.model).where(self.model.process_id == process_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_step(
        self,
        process_step_id: UUID,
    ) -> list[ScreeningDocumentReview]:
        """
        List all document reviews for a specific step.

        Args:
            process_step_id: The process step UUID.

        Returns:
            List of document reviews for the step.
        """
        query = select(self.model).where(self.model.process_step_id == process_step_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_required_document(
        self,
        required_document_id: UUID,
    ) -> ScreeningDocumentReview | None:
        """
        Get review by required document ID.

        Args:
            required_document_id: The required document UUID.

        Returns:
            Latest review for the document or None.
        """
        query = (
            select(self.model)
            .where(self.model.required_document_id == required_document_id)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_reviews(
        self,
        process_id: UUID,
    ) -> list[ScreeningDocumentReview]:
        """
        Get all pending (unreviewed) documents for a process.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of pending reviews.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == DocumentReviewStatus.PENDING)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_rejected_reviews(
        self,
        process_id: UUID,
    ) -> list[ScreeningDocumentReview]:
        """
        Get all rejected document reviews for a process.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of rejected reviews.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == DocumentReviewStatus.REJECTED)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_alert_reviews(
        self,
        process_id: UUID,
    ) -> list[ScreeningDocumentReview]:
        """
        Get all alert document reviews for a process.

        Args:
            process_id: The screening process UUID.

        Returns:
            List of reviews with ALERT status.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == DocumentReviewStatus.ALERT)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def are_all_approved(
        self,
        process_id: UUID,
    ) -> bool:
        """
        Check if all document reviews are approved.

        Args:
            process_id: The screening process UUID.

        Returns:
            True if all reviews are APPROVED.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status != DocumentReviewStatus.APPROVED)
        )
        result = await self.session.execute(query)
        non_approved = result.scalar_one_or_none()
        return non_approved is None

    async def has_rejections(
        self,
        process_id: UUID,
    ) -> bool:
        """
        Check if any documents were rejected.

        Args:
            process_id: The screening process UUID.

        Returns:
            True if any reviews are REJECTED.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == DocumentReviewStatus.REJECTED)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def has_alerts(
        self,
        process_id: UUID,
    ) -> bool:
        """
        Check if any documents have alerts.

        Args:
            process_id: The screening process UUID.

        Returns:
            True if any reviews are ALERT.
        """
        query = (
            select(self.model)
            .where(self.model.process_id == process_id)
            .where(self.model.status == DocumentReviewStatus.ALERT)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def bulk_create(
        self,
        reviews: list[ScreeningDocumentReview],
    ) -> list[ScreeningDocumentReview]:
        """
        Create multiple reviews at once.

        Args:
            reviews: List of reviews to create.

        Returns:
            List of created reviews.
        """
        self.session.add_all(reviews)
        await self.session.flush()
        for review in reviews:
            await self.session.refresh(review)
        return reviews
