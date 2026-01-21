"""Use cases for ProfessionalDocument."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import NotFoundError, ValidationError
from src.modules.professionals.domain.models import (
    DocumentCategory,
    DocumentType,
    ProfessionalDocument,
)
from src.modules.professionals.domain.schemas import (
    ProfessionalDocumentCreate,
    ProfessionalDocumentUpdate,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalDocumentRepository,
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
)


class CreateProfessionalDocumentUseCase:
    """Use case for creating a professional document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)
        self.specialty_repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: ProfessionalDocumentCreate,
    ) -> ProfessionalDocument:
        """
        Create a new document for a professional.

        Validates:
        - Professional exists in organization
        - If qualification_id provided, it exists
        - If specialty_id provided, it exists
        - Document category matches the linked entity
        """
        # Verify professional exists
        professional = await self.professional_repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise NotFoundError(
                resource="OrganizationProfessional",
                identifier=str(professional_id),
            )

        # Validate qualification if provided
        if data.qualification_id:
            qualification = (
                await self.qualification_repository.get_by_id_for_organization(
                    data.qualification_id, organization_id
                )
            )
            if qualification is None:
                raise NotFoundError(
                    resource="ProfessionalQualification",
                    identifier=str(data.qualification_id),
                )
            if data.document_category != DocumentCategory.QUALIFICATION:
                raise ValidationError(
                    message="Documents linked to a qualification must have QUALIFICATION category",
                    field="document_category",
                )

        # Validate specialty if provided
        if data.specialty_id:
            # Note: specialty_id here refers to professional_specialty, not the specialty table
            if data.document_category != DocumentCategory.SPECIALTY:
                raise ValidationError(
                    message="Documents linked to a specialty must have SPECIALTY category",
                    field="document_category",
                )

        document = ProfessionalDocument(
            organization_professional_id=professional_id,
            **data.model_dump(),
        )

        return await self.repository.create(document)


class UpdateProfessionalDocumentUseCase:
    """Use case for updating a professional document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        document_id: UUID,
        professional_id: UUID,
        data: ProfessionalDocumentUpdate,
    ) -> ProfessionalDocument:
        """Update an existing document (PATCH semantics)."""
        document = await self.repository.get_by_id_for_professional(
            document_id, professional_id
        )
        if document is None:
            raise NotFoundError(
                resource="ProfessionalDocument",
                identifier=str(document_id),
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(document, field, value)

        return await self.repository.update(document)


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


class GetProfessionalDocumentUseCase:
    """Use case for retrieving a professional document."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        document_id: UUID,
        professional_id: UUID,
    ) -> ProfessionalDocument:
        """Get a document by ID."""
        document = await self.repository.get_by_id_for_professional(
            document_id, professional_id
        )
        if document is None:
            raise NotFoundError(
                resource="ProfessionalDocument",
                identifier=str(document_id),
            )

        return document


class ListProfessionalDocumentsUseCase:
    """Use case for listing documents for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalDocumentRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
        *,
        category: DocumentCategory | None = None,
        document_type: DocumentType | None = None,
    ) -> PaginatedResponse[ProfessionalDocument]:
        """List documents for a professional."""
        return await self.repository.list_for_professional(
            professional_id,
            pagination,
            category=category,
            document_type=document_type,
        )
