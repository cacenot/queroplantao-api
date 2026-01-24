"""Use case for creating an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ProfessionalCpfExistsError, ProfessionalEmailExistsError
from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.schemas import OrganizationProfessionalCreate
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class CreateOrganizationProfessionalUseCase:
    """
    Use case for creating a new professional in an organization.

    Validates:
    - CPF uniqueness within the organization family (parent + children/siblings)
    - Email uniqueness within the organization family
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        data: OrganizationProfessionalCreate,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        created_by: UUID | None = None,
    ) -> OrganizationProfessional:
        """
        Create a new professional in the organization.

        Args:
            organization_id: The organization UUID.
            data: The professional data.
            family_org_ids: List of all organization IDs in the family.
            created_by: UUID of the user creating this record.

        Returns:
            The created professional.

        Raises:
            ProfessionalCpfExistsError: If CPF already exists in the family.
            ProfessionalEmailExistsError: If email already exists in the family.
        """
        # Validate CPF uniqueness within the family
        if data.cpf:
            if await self.repository.exists_by_cpf_in_family(
                cpf=data.cpf,
                family_org_ids=family_org_ids,
            ):
                raise ProfessionalCpfExistsError()

        # Validate email uniqueness within the family
        if data.email:
            if await self.repository.exists_by_email_in_family(
                email=data.email,
                family_org_ids=family_org_ids,
            ):
                raise ProfessionalEmailExistsError()

        # Create the professional entity
        professional = OrganizationProfessional(
            organization_id=organization_id,
            created_by=created_by,
            **data.model_dump(),
        )

        return await self.repository.create(professional)
