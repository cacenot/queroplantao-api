"""Use cases for ProfessionalSpecialty."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ConflictError, NotFoundError
from src.modules.professionals.domain.models import ProfessionalSpecialty
from src.modules.professionals.domain.schemas import (
    ProfessionalSpecialtyCreate,
    ProfessionalSpecialtyUpdate,
)
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
    ProfessionalSpecialtyRepository,
    SpecialtyRepository,
)


class CreateProfessionalSpecialtyUseCase:
    """Use case for creating a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)
        self.qualification_repository = ProfessionalQualificationRepository(session)
        self.specialty_repository = SpecialtyRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        data: ProfessionalSpecialtyCreate,
    ) -> ProfessionalSpecialty:
        """
        Create a new specialty for a qualification.

        Validates:
        - Qualification exists in organization
        - Specialty exists
        - Specialty is not already assigned to this qualification
        """
        # Verify qualification exists
        qualification = await self.qualification_repository.get_by_id_for_organization(
            qualification_id, organization_id
        )
        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        # Verify specialty exists
        specialty = await self.specialty_repository.get_by_id(data.specialty_id)
        if specialty is None:
            raise NotFoundError(
                resource="Specialty",
                identifier=str(data.specialty_id),
            )

        # Check specialty not already assigned
        if await self.repository.specialty_exists_for_qualification(
            qualification_id, data.specialty_id
        ):
            raise ConflictError(
                resource="ProfessionalSpecialty",
                field="specialty_id",
                value=str(data.specialty_id),
                message="This specialty is already assigned to this qualification",
            )

        professional_specialty = ProfessionalSpecialty(
            qualification_id=qualification_id,
            **data.model_dump(),
        )

        return await self.repository.create(professional_specialty)


class UpdateProfessionalSpecialtyUseCase:
    """Use case for updating a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_specialty_id: UUID,
        qualification_id: UUID,
        data: ProfessionalSpecialtyUpdate,
    ) -> ProfessionalSpecialty:
        """Update an existing professional specialty (PATCH semantics)."""
        professional_specialty = await self.repository.get_by_id_for_qualification(
            professional_specialty_id, qualification_id
        )
        if professional_specialty is None:
            raise NotFoundError(
                resource="ProfessionalSpecialty",
                identifier=str(professional_specialty_id),
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(professional_specialty, field, value)

        return await self.repository.update(professional_specialty)


class DeleteProfessionalSpecialtyUseCase:
    """Use case for soft-deleting a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_specialty_id: UUID,
        qualification_id: UUID,
    ) -> None:
        """Soft delete a professional specialty."""
        professional_specialty = await self.repository.get_by_id_for_qualification(
            professional_specialty_id, qualification_id
        )
        if professional_specialty is None:
            raise NotFoundError(
                resource="ProfessionalSpecialty",
                identifier=str(professional_specialty_id),
            )

        await self.repository.soft_delete(professional_specialty_id)


class GetProfessionalSpecialtyUseCase:
    """Use case for retrieving a professional specialty."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        professional_specialty_id: UUID,
        qualification_id: UUID,
    ) -> ProfessionalSpecialty:
        """Get a professional specialty by ID with specialty data loaded."""
        professional_specialty = await self.repository.get_by_id_with_specialty(
            professional_specialty_id, qualification_id
        )
        if professional_specialty is None:
            raise NotFoundError(
                resource="ProfessionalSpecialty",
                identifier=str(professional_specialty_id),
            )

        return professional_specialty


class ListProfessionalSpecialtiesUseCase:
    """Use case for listing specialties for a qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalSpecialtyRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ProfessionalSpecialty]:
        """List specialties for a qualification."""
        return await self.repository.list_for_qualification(
            qualification_id, pagination
        )
