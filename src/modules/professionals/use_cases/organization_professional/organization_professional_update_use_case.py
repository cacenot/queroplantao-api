"""Use case for updating an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ConflictError, NotFoundError
from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.schemas import OrganizationProfessionalUpdate
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class UpdateOrganizationProfessionalUseCase:
    """
    Use case for updating an existing professional in an organization.

    Supports partial updates (PATCH semantics).
    Validates:
    - Professional exists in the organization
    - CPF uniqueness (if changed)
    - Email uniqueness (if changed)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: OrganizationProfessionalUpdate,
        updated_by: UUID | None = None,
    ) -> OrganizationProfessional:
        """
        Update an existing professional.

        Args:
            professional_id: The professional UUID to update.
            organization_id: The organization UUID.
            data: The partial update data.
            updated_by: UUID of the user updating this record.

        Returns:
            The updated professional.

        Raises:
            NotFoundError: If professional not found in organization.
            ConflictError: If CPF or email already exists.
        """
        # Get the existing professional
        professional = await self.repository.get_by_id_for_organization(
            professional_id, organization_id
        )
        if professional is None:
            raise NotFoundError(
                resource="OrganizationProfessional",
                identifier=str(professional_id),
            )

        # Get update data (only fields that were explicitly set)
        update_data = data.model_dump(exclude_unset=True)

        # Validate CPF uniqueness if being changed
        if "cpf" in update_data and update_data["cpf"] != professional.cpf:
            cpf = update_data["cpf"]
            if cpf and await self.repository.exists_by_cpf(
                cpf, organization_id, exclude_id=professional_id
            ):
                raise ConflictError(
                    resource="OrganizationProfessional",
                    field="cpf",
                    value=cpf,
                    message="A professional with this CPF already exists in the organization",
                )

        # Validate email uniqueness if being changed
        if "email" in update_data and update_data["email"] != professional.email:
            email = update_data["email"]
            if email and await self.repository.exists_by_email(
                email, organization_id, exclude_id=professional_id
            ):
                raise ConflictError(
                    resource="OrganizationProfessional",
                    field="email",
                    value=email,
                    message="A professional with this email already exists in the organization",
                )

        # Apply updates
        for field, value in update_data.items():
            setattr(professional, field, value)

        # Track who updated
        if updated_by:
            professional.updated_by = updated_by

        return await self.repository.update(professional)
