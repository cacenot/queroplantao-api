"""Use case for creating an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ConflictError
from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.schemas import OrganizationProfessionalCreate
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class CreateOrganizationProfessionalUseCase:
    """
    Use case for creating a new professional in an organization.

    Validates:
    - CPF uniqueness within the organization
    - Email uniqueness within the organization
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        data: OrganizationProfessionalCreate,
        created_by: UUID | None = None,
    ) -> OrganizationProfessional:
        """
        Create a new professional in the organization.

        Args:
            organization_id: The organization UUID.
            data: The professional data.
            created_by: UUID of the user creating this record.

        Returns:
            The created professional.

        Raises:
            ConflictError: If CPF or email already exists in the organization.
        """
        # Validate CPF uniqueness
        if data.cpf:
            if await self.repository.exists_by_cpf(data.cpf, organization_id):
                raise ConflictError(
                    resource="OrganizationProfessional",
                    field="cpf",
                    value=data.cpf,
                    message="A professional with this CPF already exists in the organization",
                )

        # Validate email uniqueness
        if data.email:
            if await self.repository.exists_by_email(data.email, organization_id):
                raise ConflictError(
                    resource="OrganizationProfessional",
                    field="email",
                    value=data.email,
                    message="A professional with this email already exists in the organization",
                )

        # Create the professional entity
        professional = OrganizationProfessional(
            organization_id=organization_id,
            created_by=created_by,
            **data.model_dump(),
        )

        return await self.repository.create(professional)
