"""Use case for soft-deleting a professional document."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import DocumentNotFoundError
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)


class DeleteProfessionalDocumentUseCase:
    """Use case for soft-deleting a professional document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        document_id: UUID,
        professional_id: UUID,
        organization_id: UUID | None = None,
        deleted_by: UUID | None = None,
    ) -> None:
        """
        Soft delete a document.

        Args:
            document_id: The document UUID to delete.
            professional_id: The professional UUID.
            organization_id: The organization UUID (unused, for API consistency).
            deleted_by: UUID of the user deleting this record (unused, for future audit).
        """
        document = await self.repository.get_by_id_for_professional(
            document_id, professional_id
        )
        if document is None:
            raise DocumentNotFoundError()

        await self.repository.soft_delete(document_id)
