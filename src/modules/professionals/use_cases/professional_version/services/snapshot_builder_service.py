"""Service for building snapshots from professional entities.

Converts OrganizationProfessional and related entities into
a ProfessionalDataSnapshot structure for storage.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import OrganizationProfessional
from src.modules.professionals.domain.models.version_snapshot import (
    BankAccountSnapshot,
    CompanySnapshot,
    EducationSnapshot,
    PersonalInfoSnapshot,
    ProfessionalDataSnapshot,
    QualificationSnapshot,
    SpecialtySnapshot,
)
from src.modules.professionals.infrastructure.repositories import (
    OrganizationProfessionalRepository,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models import (
        ProfessionalCompany,
        ProfessionalEducation,
        ProfessionalQualification,
        ProfessionalSpecialty,
    )
    from src.shared.domain.models import BankAccount


class SnapshotBuilderService:
    """
    Service for building professional data snapshots.

    Converts entity state into snapshot format for version storage.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.professional_repository = OrganizationProfessionalRepository(session)

    async def build_snapshot_for_professional(
        self,
        professional_id: UUID,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None = None,
    ) -> ProfessionalDataSnapshot | None:
        """
        Build a complete snapshot from current professional data.

        Args:
            professional_id: The professional UUID.
            organization_id: The organization UUID.
            family_org_ids: Family organization IDs for scope.

        Returns:
            Complete snapshot or None if professional not found.
        """
        professional = await self.professional_repository.get_by_id_with_relations(
            id=professional_id,
            organization_id=organization_id,
            family_org_ids=family_org_ids,
        )

        if professional is None:
            return None

        return self.build_snapshot_from_entity(professional)

    def build_snapshot_from_entity(
        self,
        professional: OrganizationProfessional,
    ) -> ProfessionalDataSnapshot:
        """
        Build snapshot from a loaded professional entity.

        Args:
            professional: Professional entity with relations loaded.

        Returns:
            Complete snapshot.
        """
        snapshot: ProfessionalDataSnapshot = {
            "personal_info": self._build_personal_info(professional),
        }

        # Add qualifications if loaded
        if professional.qualifications:
            snapshot["qualifications"] = [
                self._build_qualification(q) for q in professional.qualifications
            ]

        # Add companies if loaded
        if professional.professional_companies:
            snapshot["companies"] = [
                self._build_company(pc) for pc in professional.professional_companies
            ]

        # Add bank accounts if loaded
        if professional.bank_accounts:
            snapshot["bank_accounts"] = [
                self._build_bank_account(ba) for ba in professional.bank_accounts
            ]

        return snapshot

    def _build_personal_info(
        self,
        professional: OrganizationProfessional,
    ) -> PersonalInfoSnapshot:
        """Build personal info snapshot from professional."""
        info: PersonalInfoSnapshot = {
            "full_name": professional.full_name,
            "is_verified": professional.verified_at is not None,
        }

        # Optional fields
        if professional.email:
            info["email"] = professional.email
        if professional.phone:
            info["phone"] = professional.phone
        if professional.cpf:
            info["cpf"] = professional.cpf
        if professional.birth_date:
            info["birth_date"] = professional.birth_date
        if professional.nationality:
            info["nationality"] = professional.nationality
        if professional.gender:
            info["gender"] = professional.gender.value
        if professional.marital_status:
            info["marital_status"] = professional.marital_status.value
        if professional.avatar_url:
            info["avatar_url"] = professional.avatar_url

        # Address fields
        if professional.address:
            info["address"] = professional.address
        if professional.number:
            info["number"] = professional.number
        if professional.complement:
            info["complement"] = professional.complement
        if professional.neighborhood:
            info["neighborhood"] = professional.neighborhood
        if professional.city:
            info["city"] = professional.city
        if professional.state_code:
            info["state_code"] = professional.state_code
        if professional.postal_code:
            info["postal_code"] = professional.postal_code

        # Verification
        if professional.verified_at:
            info["verified_at"] = professional.verified_at.isoformat()

        return info

    def _build_qualification(
        self, qualification: "ProfessionalQualification"
    ) -> QualificationSnapshot:
        """Build qualification snapshot."""
        snapshot: QualificationSnapshot = {
            "id": str(qualification.id),
            "professional_type": qualification.professional_type.value,
            "is_primary": qualification.is_primary or False,
            "council_type": qualification.council_type.value,
            "council_number": qualification.council_number,
            "council_state": qualification.council_state,
            "specialties": [],
            "educations": [],
        }

        if qualification.graduation_year:
            snapshot["graduation_year"] = qualification.graduation_year

        # Build specialties
        if qualification.specialties:
            snapshot["specialties"] = [
                self._build_specialty(s) for s in qualification.specialties
            ]

        # Build educations
        if qualification.educations:
            snapshot["educations"] = [
                self._build_education(e) for e in qualification.educations
            ]

        return snapshot

    def _build_specialty(self, specialty: "ProfessionalSpecialty") -> SpecialtySnapshot:
        """Build specialty snapshot."""
        snapshot: SpecialtySnapshot = {
            "id": str(specialty.id),
            "specialty_id": str(specialty.specialty_id),
            "is_primary": specialty.is_primary or False,
        }

        # Get specialty name from relationship if loaded
        if specialty.specialty and specialty.specialty.name:
            snapshot["specialty_name"] = specialty.specialty.name

        if specialty.rqe_number:
            snapshot["rqe_number"] = specialty.rqe_number
        if specialty.rqe_state:
            snapshot["rqe_state"] = specialty.rqe_state
        if specialty.residency_status:
            snapshot["residency_status"] = specialty.residency_status.value
        if specialty.residency_institution:
            snapshot["residency_institution"] = specialty.residency_institution
        if specialty.residency_expected_completion:
            snapshot["residency_expected_completion"] = (
                specialty.residency_expected_completion.isoformat()
            )
        if specialty.certificate_url:
            snapshot["certificate_url"] = specialty.certificate_url

        return snapshot

    def _build_education(self, education: "ProfessionalEducation") -> EducationSnapshot:
        """Build education snapshot."""
        snapshot: EducationSnapshot = {
            "id": str(education.id),
            "level": education.level.value,
            "course_name": education.course_name,
            "institution": education.institution,
            "is_completed": education.is_completed or False,
        }

        if education.start_year:
            snapshot["start_year"] = education.start_year
        if education.end_year:
            snapshot["end_year"] = education.end_year
        if education.workload_hours:
            snapshot["workload_hours"] = education.workload_hours
        if education.certificate_url:
            snapshot["certificate_url"] = education.certificate_url
        if education.notes:
            snapshot["notes"] = education.notes

        return snapshot

    def _build_company(self, prof_company: "ProfessionalCompany") -> CompanySnapshot:
        """Build company snapshot."""
        company = prof_company.company

        snapshot: CompanySnapshot = {
            "id": str(prof_company.id),
            "company_id": str(company.id),
            "cnpj": company.cnpj,
            "razao_social": company.legal_name,
        }

        if company.trade_name:
            snapshot["nome_fantasia"] = company.trade_name
        if company.state_registration:
            snapshot["inscricao_estadual"] = company.state_registration
        if company.municipal_registration:
            snapshot["inscricao_municipal"] = company.municipal_registration

        # Address from company
        if company.address:
            snapshot["address"] = company.address
        if company.number:
            snapshot["number"] = company.number
        if company.complement:
            snapshot["complement"] = company.complement
        if company.neighborhood:
            snapshot["neighborhood"] = company.neighborhood
        if company.city:
            snapshot["city"] = company.city
        if company.state_code:
            snapshot["state_code"] = company.state_code
        if company.postal_code:
            snapshot["postal_code"] = company.postal_code

        # Dates from junction
        if prof_company.joined_at:
            snapshot["started_at"] = prof_company.joined_at.isoformat()
        if prof_company.left_at:
            snapshot["ended_at"] = prof_company.left_at.isoformat()

        return snapshot

    def _build_bank_account(self, bank_account: "BankAccount") -> BankAccountSnapshot:
        """Build bank account snapshot."""
        snapshot: BankAccountSnapshot = {
            "id": str(bank_account.id),
            "bank_code": bank_account.bank.code if bank_account.bank else "",
            "agency_number": bank_account.agency,
            "account_number": bank_account.account_number,
            "account_holder_name": bank_account.holder_name,
            "account_holder_document": bank_account.holder_document,
            "is_primary": bank_account.is_primary or False,
            "is_company_account": bank_account.company_id is not None,
        }

        # Get bank name if loaded
        if bank_account.bank and bank_account.bank.name:
            snapshot["bank_name"] = bank_account.bank.name

        if bank_account.agency_digit:
            snapshot["agency_digit"] = bank_account.agency_digit
        if bank_account.account_digit:
            snapshot["account_digit"] = bank_account.account_digit
        if bank_account.pix_key_type:
            snapshot["pix_key_type"] = bank_account.pix_key_type.value
        if bank_account.pix_key:
            snapshot["pix_key"] = bank_account.pix_key

        return snapshot
