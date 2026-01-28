"""Service for applying snapshots to professional entities.

Takes a ProfessionalDataSnapshot and applies the changes to the
actual database entities.

Phase 1: personal_info supported.
Phase 2: qualifications with nested entities (specialties, educations).
Phase 3: companies and bank_accounts supported.
"""

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.models.version_snapshot import (
    BankAccountSnapshot,
    CompanySnapshot,
    PersonalInfoSnapshot,
    ProfessionalDataSnapshot,
    QualificationSnapshot,
)
from src.modules.professionals.domain.schemas.professional_version import (
    BankAccountInput,
    CompanyInput,
    EducationInput,
    QualificationInput,
    SpecialtyInput,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)
from src.modules.professionals.use_cases.shared.services import (
    BankAccountSyncService,
    CompanySyncService,
    QualificationSyncService,
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
        if "qualifications" in snapshot:
            await self._apply_qualifications(
                professional_id=professional_id,
                organization_id=organization_id,
                qualifications=snapshot["qualifications"],
                applied_by=applied_by,
                family_org_ids=family_org_ids,
            )

        # Phase 3: Apply companies and bank accounts
        if "companies" in snapshot:
            await self._apply_companies(
                professional_id=professional_id,
                organization_id=organization_id,
                companies=snapshot["companies"],
                applied_by=applied_by,
            )
        if "bank_accounts" in snapshot:
            await self._apply_bank_accounts(
                professional_id=professional_id,
                organization_id=organization_id,
                bank_accounts=snapshot["bank_accounts"],
                applied_by=applied_by,
            )

        await self.session.flush()

        return professional

    def _validate_snapshot_support(
        self,
        snapshot: ProfessionalDataSnapshot,
    ) -> None:
        """
        Validate that the snapshot only contains supported features.

        Phase 3: all snapshot features are supported.
        """
        return None

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

    async def _apply_qualifications(
        self,
        professional_id: UUID,
        organization_id: UUID,
        qualifications: list[QualificationSnapshot],
        applied_by: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
    ) -> None:
        """
        Apply qualifications from snapshot.

        Converts QualificationSnapshot to QualificationInput and uses
        QualificationSyncService for the actual sync.
        """
        # Convert snapshots to input schemas
        qualifications_input = [
            self._convert_qualification_snapshot(q) for q in qualifications
        ]

        # Use sync service
        sync_service = QualificationSyncService(self.session)
        await sync_service.sync_qualifications(
            professional_id=professional_id,
            organization_id=organization_id,
            qualifications_data=qualifications_input,
            family_org_ids=family_org_ids or [],
            updated_by=applied_by,
        )

    def _convert_qualification_snapshot(
        self,
        snapshot: QualificationSnapshot,
    ) -> QualificationInput:
        """Convert a QualificationSnapshot to QualificationInput."""
        from uuid import UUID as UUIDType

        from src.modules.professionals.domain.models.enums import (
            CouncilType,
            EducationLevel,
            ProfessionalType,
            ResidencyStatus,
        )
        from src.shared.domain.value_objects import StateUF

        # Convert specialties
        specialties_input: list[SpecialtyInput] = []
        for spec in snapshot.get("specialties", []):
            rqe_state_val = spec.get("rqe_state")
            specialty_input = SpecialtyInput(
                id=UUIDType(spec["id"]) if spec.get("id") else None,
                specialty_id=UUIDType(spec["specialty_id"]),
                is_primary=spec.get("is_primary", False),
                rqe_number=spec.get("rqe_number"),
                rqe_state=StateUF(rqe_state_val) if rqe_state_val else None,
                residency_status=(
                    ResidencyStatus(spec["residency_status"])
                    if spec.get("residency_status")
                    else None
                ),
                residency_institution=spec.get("residency_institution"),
                residency_expected_completion=None,  # Date parsing handled separately
                certificate_url=spec.get("certificate_url"),
            )
            specialties_input.append(specialty_input)

        # Convert educations
        educations_input: list[EducationInput] = []
        for edu in snapshot.get("educations", []):
            education_input = EducationInput(
                id=UUIDType(edu["id"]) if edu.get("id") else None,
                level=EducationLevel(edu["level"]),
                course_name=edu["course_name"],
                institution=edu["institution"],
                start_year=edu.get("start_year"),
                end_year=edu.get("end_year"),
                is_completed=edu.get("is_completed", False),
                workload_hours=edu.get("workload_hours"),
                certificate_url=edu.get("certificate_url"),
                notes=edu.get("notes"),
            )
            educations_input.append(education_input)

        return QualificationInput(
            id=UUIDType(snapshot["id"]) if snapshot.get("id") else None,
            professional_type=ProfessionalType(snapshot["professional_type"]),
            is_primary=snapshot.get("is_primary", False),
            graduation_year=snapshot.get("graduation_year"),
            council_type=CouncilType(snapshot["council_type"]),
            council_number=snapshot["council_number"],
            council_state=StateUF(snapshot["council_state"]),
            specialties=specialties_input,
            educations=educations_input,
        )

    async def _apply_companies(
        self,
        professional_id: UUID,
        organization_id: UUID,
        companies: list[CompanySnapshot],
        applied_by: UUID,
    ) -> None:
        """Apply companies from snapshot."""
        companies_input = [self._convert_company_snapshot(c) for c in companies]
        sync_service = CompanySyncService(self.session)
        await sync_service.sync_companies(
            professional_id=professional_id,
            organization_id=organization_id,
            companies_data=companies_input,
            updated_by=applied_by,
        )

    async def _apply_bank_accounts(
        self,
        professional_id: UUID,
        organization_id: UUID,
        bank_accounts: list[BankAccountSnapshot],
        applied_by: UUID,
    ) -> None:
        """Apply bank accounts from snapshot."""
        bank_accounts_input = [
            self._convert_bank_account_snapshot(b) for b in bank_accounts
        ]
        sync_service = BankAccountSyncService(self.session)
        await sync_service.sync_bank_accounts(
            professional_id=professional_id,
            organization_id=organization_id,
            bank_accounts_data=bank_accounts_input,
            updated_by=applied_by,
        )

    def _convert_company_snapshot(self, snapshot: CompanySnapshot) -> CompanyInput:
        """Convert CompanySnapshot to CompanyInput."""
        from uuid import UUID as UUIDType

        from src.shared.domain.value_objects import StateUF

        return CompanyInput(
            id=UUIDType(snapshot["id"]) if snapshot.get("id") else None,
            company_id=UUIDType(snapshot["company_id"])
            if snapshot.get("company_id")
            else None,
            cnpj=snapshot["cnpj"],
            razao_social=snapshot["razao_social"],
            nome_fantasia=snapshot.get("nome_fantasia"),
            inscricao_estadual=snapshot.get("inscricao_estadual"),
            inscricao_municipal=snapshot.get("inscricao_municipal"),
            address=snapshot.get("address"),
            number=snapshot.get("number"),
            complement=snapshot.get("complement"),
            neighborhood=snapshot.get("neighborhood"),
            city=snapshot.get("city"),
            state_code=(
                StateUF(snapshot["state_code"]) if snapshot.get("state_code") else None
            ),
            postal_code=snapshot.get("postal_code"),
            started_at=self._parse_date(snapshot.get("started_at")),
            ended_at=self._parse_date(snapshot.get("ended_at")),
        )

    def _convert_bank_account_snapshot(
        self, snapshot: BankAccountSnapshot
    ) -> BankAccountInput:
        """Convert BankAccountSnapshot to BankAccountInput."""
        from src.shared.domain.models.enums import PixKeyType

        pix_key_type = snapshot.get("pix_key_type")
        return BankAccountInput(
            id=None,
            bank_code=snapshot["bank_code"],
            agency_number=snapshot["agency_number"],
            agency_digit=snapshot.get("agency_digit"),
            account_number=snapshot["account_number"],
            account_digit=snapshot.get("account_digit"),
            account_holder_name=snapshot["account_holder_name"],
            account_holder_document=snapshot["account_holder_document"],
            pix_key_type=PixKeyType(pix_key_type) if pix_key_type else None,
            pix_key=snapshot.get("pix_key"),
            is_primary=snapshot.get("is_primary", False),
            is_company_account=snapshot.get("is_company_account", False),
        )

    def _parse_date(self, value: str | None) -> date | None:
        if value is None:
            return None
        return date.fromisoformat(value)
