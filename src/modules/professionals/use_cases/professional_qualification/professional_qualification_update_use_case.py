"""Use case for updating a professional qualification."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ConflictError, NotFoundError
from src.modules.professionals.domain.models import ProfessionalQualification
from src.modules.professionals.domain.schemas import ProfessionalQualificationUpdate
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalQualificationRepository,
)


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
        professional_id: UUID | None = None,
        updated_by: UUID | None = None,
    ) -> ProfessionalQualification:
        """
        Update an existing qualification (PATCH semantics).

        Args:
            qualification_id: The qualification UUID to update.
            organization_id: The organization UUID.
            data: The partial update data.
            professional_id: The professional UUID (unused, for API consistency).
            updated_by: UUID of the user updating this record.
        """
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
