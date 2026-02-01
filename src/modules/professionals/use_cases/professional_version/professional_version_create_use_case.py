"""Use case for creating a professional version."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    ProfessionalCpfExistsError,
    ProfessionalEmailExistsError,
    ProfessionalNotFoundError,
)
from src.modules.professionals.domain.models.professional_version import (
    ProfessionalVersion,
)
from src.modules.professionals.domain.models.version_snapshot import (
    ProfessionalDataSnapshot,
)
from src.modules.professionals.domain.schemas.professional_version import (
    PersonalInfoInput,
    ProfessionalVersionCreate,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
    ProfessionalChangeDiffRepository,
    ProfessionalVersionRepository,
)
from src.modules.professionals.use_cases.professional_version.services import (
    DiffCalculatorService,
    SnapshotBuilderService,
)
from src.modules.screening.domain.models.enums import SourceType


class CreateProfessionalVersionUseCase:
    """
    Use case for creating a new professional version.

    Creates a version with the provided snapshot data. If source_type is DIRECT,
    the version is immediately applied. For SCREENING or other sources, the
    version remains pending until explicitly applied.

    Validations performed:
    - Professional exists
    - CPF uniqueness within family (if provided in snapshot)
    - Email uniqueness within family (if provided in snapshot)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.professional_repository = OrganizationProfessionalRepository(session)
        self.version_repository = ProfessionalVersionRepository(session)
        self.diff_repository = ProfessionalChangeDiffRepository(session)
        self.snapshot_builder = SnapshotBuilderService(session)
        self.diff_calculator = DiffCalculatorService()

    async def execute(
        self,
        organization_id: UUID,
        professional_id: UUID,
        data: ProfessionalVersionCreate,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        created_by: UUID,
    ) -> ProfessionalVersion:
        """
        Create a new professional version.

        Args:
            organization_id: The organization UUID.
            professional_id: The professional UUID.
            data: Version creation data with snapshot.
            family_org_ids: Family organization IDs for scope validation.
            created_by: UUID of the user creating the version.

        Returns:
            The created ProfessionalVersion.

        Raises:
            ProfessionalNotFoundError: If professional doesn't exist.
            ProfessionalCpfExistsError: If CPF conflicts in family.
            ProfessionalEmailExistsError: If email conflicts in family.
        """
        # 1. Validate professional exists
        professional = await self.professional_repository.get_by_id_for_organization(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )
        if professional is None:
            raise ProfessionalNotFoundError()

        # 2. Validate uniqueness rules from personal_info
        if data.personal_info:
            await self._validate_uniqueness(
                family_org_ids=family_org_ids,
                professional_id=professional_id,
                personal_info=data.personal_info,
            )

        # 3. Build current snapshot for diff calculation
        current_snapshot = await self.snapshot_builder.build_snapshot_for_professional(
            professional_id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        # 4. Build new snapshot from input
        new_snapshot = self._build_snapshot_from_input(data)

        # 5. Create version
        version = ProfessionalVersion(
            organization_id=organization_id,
            professional_id=professional_id,
            data_snapshot=new_snapshot,  # type: ignore[arg-type]
            source_type=data.source_type,
            source_id=data.source_id,
            notes=data.notes,
            created_by=created_by,
            is_current=False,
        )

        # 6. For DIRECT source, mark as applied immediately
        if data.source_type == SourceType.DIRECT:
            version.applied_at = datetime.now(timezone.utc)
            version.applied_by = created_by
            # Note: The actual application to entities happens via ApplyProfessionalVersionUseCase
            # which will be called after version creation

        # 7. Save version to get ID
        await self.version_repository.create(version)
        await self.session.flush()

        # 8. Calculate and save diffs
        diffs = self.diff_calculator.calculate_diffs(
            version_id=version.id,
            organization_id=organization_id,
            old_snapshot=current_snapshot,
            new_snapshot=new_snapshot,
        )

        if diffs:
            await self.diff_repository.create_many(diffs)

        # 9. If DIRECT, apply the version
        if data.source_type == SourceType.DIRECT:
            from src.modules.professionals.use_cases.professional_version.professional_version_apply_use_case import (
                ApplyProfessionalVersionUseCase,
            )

            apply_use_case = ApplyProfessionalVersionUseCase(self.session)
            await apply_use_case.execute(
                organization_id=organization_id,
                version_id=version.id,
                applied_by=created_by,
                family_org_ids=family_org_ids,
                skip_status_check=True,  # Already marked as applied
            )

        await self.session.flush()

        return version

    async def _validate_uniqueness(
        self,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        professional_id: UUID,
        personal_info: PersonalInfoInput,
    ) -> None:
        """Validate CPF and email uniqueness within family."""
        if personal_info.cpf:
            if await self.professional_repository.exists_by_cpf_in_family(
                cpf=personal_info.cpf,
                family_org_ids=family_org_ids,
                exclude_id=professional_id,
            ):
                raise ProfessionalCpfExistsError()

        if personal_info.email:
            if await self.professional_repository.exists_by_email_in_family(
                email=personal_info.email,
                family_org_ids=family_org_ids,
                exclude_id=professional_id,
            ):
                raise ProfessionalEmailExistsError()

    def _build_snapshot_from_input(
        self,
        data: ProfessionalVersionCreate,
    ) -> ProfessionalDataSnapshot:
        """Convert input data to snapshot format."""
        snapshot: ProfessionalDataSnapshot = {}

        if data.personal_info:
            # type: ignore because we're building a dict compatible with TypedDict
            snapshot["personal_info"] = self._convert_personal_info(  # type: ignore[typeddict-item]
                data.personal_info
            )

        if data.qualifications:
            snapshot["qualifications"] = [  # type: ignore[typeddict-item]
                self._convert_to_dict(q) for q in data.qualifications
            ]

        if data.companies:
            snapshot["companies"] = [  # type: ignore[typeddict-item]
                self._convert_to_dict(c) for c in data.companies
            ]

        if data.bank_accounts:
            snapshot["bank_accounts"] = [  # type: ignore[typeddict-item]
                self._convert_to_dict(ba) for ba in data.bank_accounts
            ]

        return snapshot

    def _convert_personal_info(self, info: PersonalInfoInput) -> dict[str, Any]:
        """Convert PersonalInfoInput to snapshot dict."""
        result: dict[str, Any] = {
            "full_name": info.full_name,
            "is_verified": info.is_verified,
        }

        # Add optional fields
        if info.email:
            result["email"] = info.email
        if info.phone:
            result["phone"] = info.phone
        if info.cpf:
            result["cpf"] = info.cpf
        if info.birth_date:
            result["birth_date"] = info.birth_date.isoformat()
        if info.nationality:
            result["nationality"] = info.nationality
        if info.gender:
            result["gender"] = info.gender.value
        if info.marital_status:
            result["marital_status"] = info.marital_status.value
        if info.avatar_url:
            result["avatar_url"] = str(info.avatar_url)
        if info.address:
            result["address"] = info.address
        if info.number:
            result["number"] = info.number
        if info.complement:
            result["complement"] = info.complement
        if info.neighborhood:
            result["neighborhood"] = info.neighborhood
        if info.city:
            result["city"] = info.city
        if info.state_code:
            result["state_code"] = str(info.state_code)
        if info.postal_code:
            result["postal_code"] = info.postal_code

        return result

    def _convert_to_dict(self, obj: Any) -> dict[str, Any]:
        """Convert a Pydantic model to dict, handling special types."""
        data: dict[str, Any] = obj.model_dump(exclude_unset=False, exclude_none=True)

        # Convert UUIDs to strings
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, list):
                data[key] = [
                    self._convert_to_dict(item) if hasattr(item, "model_dump") else item
                    for item in value
                ]
            elif hasattr(value, "value"):  # Enum
                data[key] = value.value

        return data
