"""Use case for soft-deleting a professional document."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError
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
    ) -> None:
        """Soft delete a document."""
        document = await self.repository.get_by_id_for_professional(
            document_id, professional_id
        )
        if document is None:
            raise NotFoundError(
                resource="ProfessionalDocument",
                identifier=str(document_id),
            )

        await self.repository.soft_delete(document_id)
