"""
Select documents use case.

Handles Step 2 (Document Selection) - Selecting which documents
are required for the screening.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models import ScreeningRequiredDocument
from src.modules.screening.domain.schemas import (
    ScreeningRequiredDocumentCreate,
    ScreeningRequiredDocumentResponse,
)
from src.modules.screening.infrastructure.repositories import (
    ScreeningProcessRepository,
    ScreeningRequiredDocumentRepository,
)
from src.shared.infrastructure.repositories import DocumentTypeRepository


class SelectDocumentsUseCase:
    """
    Select required documents for a screening process (Step 2).

    Adds or updates the list of required documents.
    Can also link existing professional documents.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.document_repository = ScreeningRequiredDocumentRepository(session)
        self.doc_type_repository = DocumentTypeRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        documents: list[ScreeningRequiredDocumentCreate],
        updated_by: UUID,
    ) -> list[ScreeningRequiredDocumentResponse]:
        """
        Select documents for the screening process.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            documents: List of document selections.
            updated_by: The user making the selection.

        Returns:
            List of created/updated required documents.

        Raises:
            NotFoundError: If screening not found.
            ValidationError: If invalid document type.
        """
        # Verify screening exists
        process = await self.process_repository.get_by_id_for_organization(
            organization_id=organization_id,
            entity_id=screening_id,
        )
        if not process:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(resource="Triagem", identifier=str(screening_id))

        # Get existing required documents
        existing = await self.document_repository.list_by_process(screening_id)
        existing_by_type = {doc.document_type_config_id: doc for doc in existing}

        created_documents = []

        for doc_data in documents:
            # Validate document type exists
            doc_type = await self.doc_type_repository.get_by_id(
                doc_data.document_type_config_id
            )
            if not doc_type:
                from src.app.exceptions import ValidationError

                raise ValidationError(
                    message=f"Tipo de documento inválido: {doc_data.document_type_config_id}"
                )

            # Check if already exists
            if doc_data.document_type_config_id in existing_by_type:
                # Update existing
                existing_doc = existing_by_type[doc_data.document_type_config_id]
                existing_doc.notes = doc_data.notes
                existing_doc.is_required = doc_data.is_required
                if doc_data.professional_document_id:
                    existing_doc.professional_document_id = (
                        doc_data.professional_document_id
                    )
                    existing_doc.is_existing = True
                existing_doc.updated_by = updated_by
                await self.session.flush()
                await self.session.refresh(existing_doc)
                created_documents.append(existing_doc)
            else:
                # Create new
                required_doc = ScreeningRequiredDocument(
                    screening_process_id=screening_id,
                    document_type_config_id=doc_data.document_type_config_id,
                    professional_document_id=doc_data.professional_document_id,
                    notes=doc_data.notes,
                    is_required=doc_data.is_required,
                    is_existing=doc_data.professional_document_id is not None,
                    created_by=updated_by,
                    updated_by=updated_by,
                )
                created_doc = await self.document_repository.create(required_doc)
                created_documents.append(created_doc)

        return [
            ScreeningRequiredDocumentResponse.model_validate(doc)
            for doc in created_documents
        ]


class RemoveRequiredDocumentUseCase:
    """Remove a required document from a screening."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.process_repository = ScreeningProcessRepository(session)
        self.document_repository = ScreeningRequiredDocumentRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        screening_id: UUID,
        document_id: UUID,
    ) -> None:
        """
        Remove a required document.

        Args:
            organization_id: The organization ID.
            screening_id: The screening process ID.
            document_id: The required document ID to remove.

        Raises:
            NotFoundError: If screening or document not found.
            ValidationError: If document already has uploads.
        """
        # Verify screening exists
        process = await self.process_repository.get_by_id_for_organization(
            organization_id=organization_id,
            entity_id=screening_id,
        )
        if not process:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(resource="Triagem", identifier=str(screening_id))

        # Get the document
        document = await self.document_repository.get_by_id(document_id)
        if not document or document.screening_process_id != screening_id:
            from src.app.exceptions import NotFoundError

            raise NotFoundError(
                resource="Documento requerido", identifier=str(document_id)
            )

        # Cannot remove if already uploaded
        if document.is_uploaded:
            from src.app.exceptions import ValidationError

            raise ValidationError(
                message="Não é possível remover documento que já possui upload"
            )

        await self.document_repository.delete(document_id)
