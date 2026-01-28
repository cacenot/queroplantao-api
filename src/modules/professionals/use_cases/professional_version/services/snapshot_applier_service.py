"""Service for applying snapshots to professional entities.

Takes a ProfessionalDataSnapshot and applies the changes to the
actual database entities.

Phase 1: Only personal_info is supported.
Phase 2: Will add qualifications with nested entities.
Phase 3: Will add companies and bank_accounts.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import VersionFeatureNotSupportedError
from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.models.version_snapshot import (
    PersonalInfoSnapshot,
    ProfessionalDataSnapshot,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)


class SnapshotApplierService:
    """
    Service for applying professional data snapshots to entities.

    Syncs the snapshot state to the database, creating, updating,
    and deleting entities as needed.
    """

    # Fields that can be applied from personal_info
    # Note: is_verified is handled separately (converted to verified_at)
    PERSONAL_INFO_FIELDS = [
        "full_name",
        "email",
        "phone",
        "cpf",
        "birth_date",
        "nationality",
        "gender",
        "marital_status",
        "avatar_url",
        "address",
        "number",
        "complement",
        "neighborhood",
        "city",
        "state_code",
        "postal_code",
    ]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def apply_snapshot(
        self,
        professional_id: UUID,
        organization_id: UUID,
        snapshot: ProfessionalDataSnapshot,
        applied_by: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
    ) -> OrganizationProfessional:
        """
        Apply a snapshot to a professional.

        Args:
            professional_id: The professional UUID.
            organization_id: The organization UUID.
            snapshot: The snapshot to apply.
            applied_by: UUID of user applying the snapshot.
            family_org_ids: Family org IDs for scope.

        Returns:
            Updated professional entity.

        Raises:
            ProfessionalNotFoundError: If professional doesn't exist.
            VersionFeatureNotSupportedError: If snapshot contains unsupported features.
        """
        # Validate snapshot support
        self._validate_snapshot_support(snapshot)

        # Get professional
        professional = await self.professional_repository.get_by_id_for_organization(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if professional is None:
            from src.app.exceptions import ProfessionalNotFoundError

            raise ProfessionalNotFoundError()

        # Apply personal info
        if "personal_info" in snapshot:
            await self._apply_personal_info(
                professional=professional,
                personal_info=snapshot["personal_info"],
                applied_by=applied_by,
            )

        # Phase 2: Apply qualifications
        # if "qualifications" in snapshot:
        #     await self._apply_qualifications(...)

        # Phase 3: Apply companies and bank accounts
        # if "companies" in snapshot:
        #     await self._apply_companies(...)
        # if "bank_accounts" in snapshot:
        #     await self._apply_bank_accounts(...)

        await self.session.flush()

        return professional

    def _validate_snapshot_support(
        self,
        snapshot: ProfessionalDataSnapshot,
    ) -> None:
        """
        Validate that the snapshot only contains supported features.

        Raises VersionFeatureNotSupportedError for unsupported features.
        """
        unsupported_features = []

        if snapshot.get("qualifications"):
            unsupported_features.append("qualifications")

        if snapshot.get("companies"):
            unsupported_features.append("companies")

        if snapshot.get("bank_accounts"):
            unsupported_features.append("bank_accounts")

        if unsupported_features:
            raise VersionFeatureNotSupportedError(
                feature=", ".join(unsupported_features)
            )

    async def _apply_personal_info(
        self,
        professional: OrganizationProfessional,
        personal_info: PersonalInfoSnapshot,
        applied_by: UUID,
    ) -> None:
        """Apply personal info fields to professional."""
        for field in self.PERSONAL_INFO_FIELDS:
            if field in personal_info:
                value = personal_info[field]  # type: ignore[literal-required]

                # Handle enum conversion for gender and marital_status
                if field == "gender" and value is not None:
                    from src.modules.professionals.domain.models.enums import Gender

                    value = Gender(value) if isinstance(value, str) else value

                if field == "marital_status" and value is not None:
                    from src.modules.professionals.domain.models.enums import (
                        MaritalStatus,
                    )

                    value = MaritalStatus(value) if isinstance(value, str) else value

                setattr(professional, field, value)

        # Handle is_verified -> verified_at conversion
        if "is_verified" in personal_info:
            is_verified = personal_info["is_verified"]
            if is_verified and professional.verified_at is None:
                # Mark as verified
                professional.verified_at = datetime.now(timezone.utc)
                professional.verified_by = applied_by
            elif not is_verified:
                # Clear verification
                professional.verified_at = None
                professional.verified_by = None

        # Update tracking
        professional.updated_by = applied_by
        professional.updated_at = datetime.now(timezone.utc)

        self.session.add(professional)
