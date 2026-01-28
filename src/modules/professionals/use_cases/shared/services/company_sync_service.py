"""Service for syncing companies from version snapshots."""

from datetime import datetime, time, timezone
from uuid import UUID

from fastapi_restkit.pagination import PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.professionals.domain.models import ProfessionalCompany
from src.modules.professionals.domain.schemas.professional_version import CompanyInput
from src.modules.professionals.infrastructure.repositories import (
    CompanyRepository,
    ProfessionalCompanyRepository,
)


class CompanySyncService:
    """
    Syncs company data between snapshot and entities.

    Matching strategy:
    - Upsert Company by CNPJ
    - Link ProfessionalCompany by company_id
    - Existing links not in snapshot: soft delete
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.professional_company_repository = ProfessionalCompanyRepository(session)

    async def sync_companies(
        self,
        professional_id: UUID,
        organization_id: UUID,
        companies_data: list[CompanyInput],
        updated_by: UUID,
    ) -> list[ProfessionalCompany]:
        existing_links = await self._get_existing_links(professional_id)
        existing_by_company_id = {link.company_id: link for link in existing_links}

        matched_ids: set[UUID] = set()
        result: list[ProfessionalCompany] = []

        for company_data in companies_data:
            company, _ = await self.company_repository.get_or_create_by_cnpj(
                cnpj=str(company_data.cnpj),
                company_data=company_data,
                created_by=updated_by,
            )

            link = existing_by_company_id.get(company.id)
            if link:
                matched_ids.add(link.id)
                updated = await self._update_link(link, company_data, updated_by)
                result.append(updated)
            else:
                created = await self._create_link(
                    professional_id, company.id, company_data, updated_by
                )
                result.append(created)

        # Soft delete links not in snapshot
        ids_to_delete = [
            link.id for link in existing_links if link.id not in matched_ids
        ]
        for link_id in ids_to_delete:
            await self.professional_company_repository.soft_delete(link_id)

        await self.session.flush()
        return result

    async def _get_existing_links(
        self, professional_id: UUID
    ) -> list[ProfessionalCompany]:
        paginated = await self.professional_company_repository.list_for_professional(
            professional_id, PaginationParams(page=1, page_size=100)
        )
        return paginated.items

    async def _create_link(
        self,
        professional_id: UUID,
        company_id: UUID,
        data: CompanyInput,
        updated_by: UUID,
    ) -> ProfessionalCompany:
        link = ProfessionalCompany(
            organization_professional_id=professional_id,
            company_id=company_id,
            joined_at=self._to_datetime(data.started_at) or datetime.now(timezone.utc),
            left_at=self._to_datetime(data.ended_at),
            created_by=updated_by,
            updated_by=updated_by,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def _update_link(
        self,
        link: ProfessionalCompany,
        data: CompanyInput,
        updated_by: UUID,
    ) -> ProfessionalCompany:
        joined_at = self._to_datetime(data.started_at)
        left_at = self._to_datetime(data.ended_at)

        if joined_at is not None:
            link.joined_at = joined_at
        if left_at is not None:
            link.left_at = left_at

        link.updated_by = updated_by
        link.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return link

    def _to_datetime(self, value) -> datetime | None:
        if value is None:
            return None
        return datetime.combine(value, time.min, tzinfo=timezone.utc)
