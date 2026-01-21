"""Use cases for ProfessionalQualification."""

from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ConflictError, NotFoundError, ValidationError
from src.modules.professionals.domain.models import (
    ProfessionalQualification,
    validate_council_for_professional_type,
)
from src.modules.professionals.domain.schemas import (
    ProfessionalQualificationCreate,
    ProfessionalQualificationUpdate,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalQualificationRepository,
)


class CreateProfessionalQualificationUseCase:
    """Use case for creating a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: ProfessionalQualificationCreate,
    ) -> ProfessionalQualification:
        """
        Create a new qualification for a professional.

        Validates:
        - Professional exists in organization
        - Council type matches professional type
        - Council registration is unique in organization
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

        # Validate council matches professional type
        if not validate_council_for_professional_type(
            data.council_type, data.professional_type
        ):
            raise ValidationError(
                message=f"Council type {data.council_type.value} is not valid for "
                f"professional type {data.professional_type.value}",
                field="council_type",
            )

        # Validate council uniqueness in organization
        if await self.repository.council_exists_in_organization(
            data.council_number, data.council_state, organization_id
        ):
            raise ConflictError(
                resource="ProfessionalQualification",
                field="council_number",
                value=f"{data.council_number}/{data.council_state}",
                message="This council registration already exists in the organization",
            )

        qualification = ProfessionalQualification(
            organization_id=organization_id,
            organization_professional_id=professional_id,
            **data.model_dump(),
        )

        return await self.repository.create(qualification)


class UpdateProfessionalQualificationUseCase:
    """Use case for updating a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        data: ProfessionalQualificationUpdate,
    ) -> ProfessionalQualification:
        """Update an existing qualification (PATCH semantics)."""
        qualification = await self.repository.get_by_id_for_organization(
            qualification_id, organization_id
        )
        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate council uniqueness if changing
        council_number = update_data.get("council_number", qualification.council_number)
        council_state = update_data.get("council_state", qualification.council_state)

        if "council_number" in update_data or "council_state" in update_data:
            if await self.repository.council_exists_in_organization(
                council_number,
                council_state,
                organization_id,
                exclude_id=qualification_id,
            ):
                raise ConflictError(
                    resource="ProfessionalQualification",
                    field="council_number",
                    value=f"{council_number}/{council_state}",
                    message="This council registration already exists in the organization",
                )

        for field, value in update_data.items():
            setattr(qualification, field, value)

        return await self.repository.update(qualification)


class DeleteProfessionalQualificationUseCase:
    """Use case for soft-deleting a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
    ) -> None:
        """Soft delete a qualification."""
        qualification = await self.repository.get_by_id_for_organization(
            qualification_id, organization_id
        )
        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        await self.repository.soft_delete(qualification_id)


class GetProfessionalQualificationUseCase:
    """Use case for retrieving a professional qualification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        qualification_id: UUID,
        organization_id: UUID,
        *,
        include_relations: bool = False,
    ) -> ProfessionalQualification:
        """Get a qualification by ID."""
        if include_relations:
            qualification = await self.repository.get_by_id_with_relations(
                qualification_id, organization_id
            )
        else:
            qualification = await self.repository.get_by_id_for_organization(
                qualification_id, organization_id
            )

        if qualification is None:
            raise NotFoundError(
                resource="ProfessionalQualification",
                identifier=str(qualification_id),
            )

        return qualification


class ListProfessionalQualificationsUseCase:
    """Use case for listing qualifications for a professional."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfessionalQualificationRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ProfessionalQualification]:
        """List qualifications for a professional."""
        return await self.repository.list_for_professional(professional_id, pagination)
