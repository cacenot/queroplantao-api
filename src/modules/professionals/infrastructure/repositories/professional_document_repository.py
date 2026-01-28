"""ProfessionalDocument repository for database operations."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.professionals.domain.models import ProfessionalDocument
from src.modules.professionals.infrastructure.filters import (
    ProfessionalDocumentFilter,
    ProfessionalDocumentSorting,
)
from src.shared.domain.models import DocumentCategory, DocumentType
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeletePaginationMixin,
)


class ProfessionalDocumentRepository(
    SoftDeletePaginationMixin[ProfessionalDocument],
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
        return self._exclude_deleted().where(
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

    async def list_for_professional(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalDocumentFilter | None = None,
        sorting: ProfessionalDocumentSorting | None = None,
    ) -> PaginatedResponse[ProfessionalDocument]:
        """
        List documents for a professional with pagination, filtering, and sorting.

        Args:
            professional_id: The organization professional UUID.
            pagination: Pagination parameters.
            filters: Optional filters (search, document_type, document_category, is_verified).
            sorting: Optional sorting (id, document_type, file_name, expires_at, created_at).

        Returns:
            Paginated list of documents.
        """
        query = self._base_query_for_professional(professional_id)
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

    async def list_for_qualification(
        self,
        qualification_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalDocumentFilter | None = None,
        sorting: ProfessionalDocumentSorting | None = None,
    ) -> PaginatedResponse[ProfessionalDocument]:
        """
        List documents for a qualification.

        Args:
            qualification_id: The qualification UUID.
            pagination: Pagination parameters.
            filters: Optional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of documents.
        """
        query = self._exclude_deleted().where(
            ProfessionalDocument.qualification_id == qualification_id
        )
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

    async def list_for_specialty(
        self,
        specialty_id: UUID,
        pagination: PaginationParams,
        *,
        filters: ProfessionalDocumentFilter | None = None,
        sorting: ProfessionalDocumentSorting | None = None,
    ) -> PaginatedResponse[ProfessionalDocument]:
        """
        List documents for a professional specialty.

        Args:
            specialty_id: The professional specialty UUID.
            pagination: Pagination parameters.
            filters: Optional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of documents.
        """
        query = self._exclude_deleted().where(
            ProfessionalDocument.specialty_id == specialty_id
        )
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

    async def list_by_category(
        self,
        professional_id: UUID,
        category: DocumentCategory,
        pagination: PaginationParams,
        *,
        filters: ProfessionalDocumentFilter | None = None,
        sorting: ProfessionalDocumentSorting | None = None,
    ) -> PaginatedResponse[ProfessionalDocument]:
        """
        List documents by category for a professional.

        Args:
            professional_id: The organization professional UUID.
            category: The document category.
            pagination: Pagination parameters.
            filters: Optional additional filters.
            sorting: Optional sorting.

        Returns:
            Paginated list of documents.
        """
        query = (
            self._base_query_for_professional(professional_id)
            .join(DocumentType)
            .where(DocumentType.category == category)
            .options(selectinload(ProfessionalDocument.document_type))
        )
        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

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
