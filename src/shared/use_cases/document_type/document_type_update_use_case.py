"""Use case for updating a document type."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import DocumentTypeNotFoundError
from src.shared.domain.models import DocumentType
from src.shared.domain.schemas.document_type import DocumentTypeUpdate
from src.shared.infrastructure.repositories.document_type_repository import (
    DocumentTypeRepository,
)
from src.shared.use_cases.document_type.cache import invalidate_document_types_cache


class UpdateDocumentTypeUseCase:
    """Use case for updating a document type (PATCH semantics)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DocumentTypeRepository(session)

    async def execute(
        self,
        document_type_id: UUID,
        organization_id: UUID,
        parent_org_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        data: DocumentTypeUpdate,
        updated_by: UUID | None = None,
    ) -> DocumentType:
        """
        Update a document type using PATCH semantics.

        Args:
            document_type_id: The document type UUID.
            organization_id: The current organization UUID.
            parent_org_id: The parent organization ID (for cache key).
            family_org_ids: All organization IDs in the family.
            data: Update data (only fields to update).
            updated_by: User ID performing the update.

        Returns:
            The updated document type.

        Raises:
            DocumentTypeNotFoundError: If document type not found.
        """
        # Get existing document type
        document_type = await self.repository.get_by_organization(
            id=document_type_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if document_type is None:
            raise DocumentTypeNotFoundError()

        # Get only the fields that were explicitly set
        update_data = data.model_dump(exclude_unset=True)

        # Apply updates
        for field, value in update_data.items():
            setattr(document_type, field, value)

        if updated_by:
            document_type.updated_by = updated_by

        result = await self.repository.update(document_type)

        # Invalidate cache
        await invalidate_document_types_cache(parent_org_id)

        return result
