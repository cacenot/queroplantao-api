"""Use case for updating an organization professional."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ProfessionalCpfExistsError,
    ProfessionalEmailExistsError,
    ProfessionalNotFoundError,
)
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
    - Professional exists in the organization family
    - CPF uniqueness within the family (if changed)
    - Email uniqueness within the family (if changed)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OrganizationProfessionalRepository(session)

    async def execute(
        self,
        professional_id: UUID,
        organization_id: UUID,
        data: OrganizationProfessionalUpdate,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        updated_by: UUID | None = None,
    ) -> OrganizationProfessional:
        """
        Update an existing professional.

        Args:
            professional_id: The professional UUID to update.
            organization_id: The organization UUID.
            data: The partial update data.
            family_org_ids: List of all organization IDs in the family.
            updated_by: UUID of the user updating this record.

        Returns:
            The updated professional.

        Raises:
            ProfessionalNotFoundError: If professional not found in organization family.
            ProfessionalCpfExistsError: If CPF already exists in the family.
            ProfessionalEmailExistsError: If email already exists in the family.
        """
        # Get the existing professional (with family scope)
        professional = await self.repository.get_by_id_for_organization(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # Get update data (only fields that were explicitly set)
        update_data = data.model_dump(exclude_unset=True)

        # Validate CPF uniqueness within the family if being changed
        if "cpf" in update_data and update_data["cpf"] != professional.cpf:
            cpf = update_data["cpf"]
            if cpf and await self.repository.exists_by_cpf_in_family(
                cpf=cpf,
                family_org_ids=family_org_ids,
                exclude_id=professional_id,
            ):
                raise ProfessionalCpfExistsError()

        # Validate email uniqueness within the family if being changed
        if "email" in update_data and update_data["email"] != professional.email:
            email = update_data["email"]
            if email and await self.repository.exists_by_email_in_family(
                email=email,
                family_org_ids=family_org_ids,
                exclude_id=professional_id,
            ):
                raise ProfessionalEmailExistsError()

        # Apply updates
        for field, value in update_data.items():
            setattr(professional, field, value)

        # Track who updated
        if updated_by:
            professional.updated_by = updated_by

        return await self.repository.update(professional)
