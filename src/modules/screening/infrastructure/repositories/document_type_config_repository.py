"""DocumentTypeConfig repository for database operations."""

from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models.enums import DocumentCategory
from src.modules.screening.domain.models import DocumentTypeConfig
from src.shared.infrastructure.repositories import (
    BaseRepository,
    SoftDeletePaginationMixin,
)


class DocumentTypeConfigRepository(
    SoftDeletePaginationMixin[DocumentTypeConfig],
    BaseRepository[DocumentTypeConfig],
):
    """
    Repository for DocumentTypeConfig model.

    Provides CRUD operations with soft delete support.
    Document types can be global (organization_id=None) or org-specific.
    """

    model = DocumentTypeConfig

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_organization(
        self,
        organization_id: UUID | None,
    ) -> Select[tuple[DocumentTypeConfig]]:
        """
        Get base query for available document types.

        Returns both global types (organization_id=None) and
        organization-specific types.

        Args:
            organization_id: The organization UUID (or None for global only).

        Returns:
            Query with soft-delete filter.
        """
        base = self._exclude_deleted()
        if organization_id is None:
            return base.where(DocumentTypeConfig.organization_id.is_(None))
        return base.where(
            (DocumentTypeConfig.organization_id.is_(None))
            | (DocumentTypeConfig.organization_id == organization_id)
        )

    async def list_available(
        self,
        organization_id: UUID | None = None,
        category: DocumentCategory | None = None,
    ) -> list[DocumentTypeConfig]:
        """
        List available document types for an organization.

        Includes global types and org-specific types.

        Args:
            organization_id: The organization UUID.
            category: Optional category filter.

        Returns:
            List of available document types.
        """
        query = self._base_query_for_organization(organization_id)
        query = query.where(DocumentTypeConfig.is_active == True)  # noqa: E712

        if category is not None:
            query = query.where(DocumentTypeConfig.category == category)

        query = query.order_by(DocumentTypeConfig.display_order)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_code(
        self,
        code: str,
    ) -> DocumentTypeConfig | None:
        """
        Get document type by code.

        Args:
            code: The unique document type code.

        Returns:
            DocumentTypeConfig if found, None otherwise.
        """
        query = self._exclude_deleted().where(DocumentTypeConfig.code == code)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_category(
        self,
        category: DocumentCategory,
        organization_id: UUID | None = None,
    ) -> list[DocumentTypeConfig]:
        """
        List document types by category.

        Args:
            category: The document category.
            organization_id: Optional org for org-specific types.

        Returns:
            List of document types in the category.
        """
        query = (
            self._base_query_for_organization(organization_id)
            .where(DocumentTypeConfig.category == category)
            .where(DocumentTypeConfig.is_active == True)  # noqa: E712
            .order_by(DocumentTypeConfig.display_order)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_for_professional_type(
        self,
        professional_type: str,
        organization_id: UUID | None = None,
    ) -> list[DocumentTypeConfig]:
        """
        List document types applicable to a professional type.

        Args:
            professional_type: The professional type value.
            organization_id: Optional org for org-specific types.

        Returns:
            List of applicable document types.
        """
        # Get all active types and filter in Python
        # (JSON array filtering is complex in SQL)
        all_types = await self.list_available(organization_id)

        applicable = []
        for doc_type in all_types:
            # If required_for is None, it applies to all types
            if doc_type.required_for_professional_types is None:
                applicable.append(doc_type)
            elif professional_type in doc_type.required_for_professional_types:
                applicable.append(doc_type)

        return applicable
