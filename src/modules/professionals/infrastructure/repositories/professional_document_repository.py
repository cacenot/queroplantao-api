"""ProfessionalDocument repository for database operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.professionals.domain.models import ProfessionalDocument
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeleteMixin,
)


class ProfessionalDocumentRepository(
    SoftDeleteMixin[ProfessionalDocument],
    BaseRepository[ProfessionalDocument],
):
    """
    Repository for ProfessionalDocument model.

    Provides CRUD operations with soft delete support.
    """

    model = ProfessionalDocument

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_professional(
        self,
        professional_id: UUID,
    ) -> Select[tuple[ProfessionalDocument]]:
        """
        Get base query filtered by professional.

        Args:
            professional_id: The organization professional UUID.

        Returns:
            Query filtered by professional and excluding soft-deleted.
        """
        return self.get_query().where(
            ProfessionalDocument.organization_professional_id == professional_id
        )

    async def get_by_id_for_professional(
        self,
        id: UUID,
        professional_id: UUID,
    ) -> ProfessionalDocument | None:
        """
        Get document by ID for a specific professional.

        Args:
            id: The document UUID.
            professional_id: The organization professional UUID.

        Returns:
            Document if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id).where(
                ProfessionalDocument.id == id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_type_for_professional(
        self,
        professional_id: UUID,
        document_type_id: UUID,
    ) -> list[ProfessionalDocument]:
        """
        Get all documents of a specific type for a professional.

        Args:
            professional_id: The organization professional UUID.
            document_type_id: The document type UUID.

        Returns:
            List of documents (may have multiple versions).
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id)
            .where(ProfessionalDocument.document_type_id == document_type_id)
            .options(selectinload(ProfessionalDocument.document_type))
        )
        return list(result.scalars().all())

    # ============================================================
    # Pending Document Methods (Screening Workflow)
    # ============================================================

    async def list_pending_by_screening(
        self,
        screening_id: UUID,
    ) -> list[ProfessionalDocument]:
        """
        List all pending documents for a screening.

        Args:
            screening_id: The screening process UUID.

        Returns:
            List of pending documents linked to the screening.
        """
        result = await self.session.execute(
            self.get_query()
            .where(ProfessionalDocument.screening_id == screening_id)
            .where(ProfessionalDocument.is_pending.is_(True))
        )
        return list(result.scalars().all())

    async def promote_pending_documents(
        self,
        screening_id: UUID,
        promoted_by: UUID,
    ) -> int:
        """
        Promote all pending documents for a screening.

        Sets is_pending=False and records promotion timestamp and user.

        Args:
            screening_id: The screening process UUID.
            promoted_by: The user promoting the documents.

        Returns:
            Number of documents promoted.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(ProfessionalDocument)
            .where(ProfessionalDocument.screening_id == screening_id)
            .where(ProfessionalDocument.is_pending.is_(True))
            .where(ProfessionalDocument.deleted_at.is_(None))
            .values(
                is_pending=False,
                promoted_at=now,
                promoted_by=promoted_by,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def soft_delete_orphan_pending_documents(
        self,
        screening_id: UUID,
        deleted_by: UUID,
    ) -> int:
        """
        Soft delete all pending documents for a cancelled/rejected screening.

        These are orphan documents that were uploaded during screening but
        never got approved.

        Args:
            screening_id: The screening process UUID.
            deleted_by: The user performing the deletion.

        Returns:
            Number of documents soft deleted.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(ProfessionalDocument)
            .where(ProfessionalDocument.screening_id == screening_id)
            .where(ProfessionalDocument.is_pending.is_(True))
            .where(ProfessionalDocument.deleted_at.is_(None))
            .values(
                deleted_at=now,
                deleted_by=deleted_by,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount
