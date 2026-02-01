"""Service for syncing bank accounts from version snapshots."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import BankNotFoundError
from src.modules.professionals.domain.schemas.professional_version import (
    BankAccountInput,
)
from src.modules.professionals.infrastructure.repositories import BankAccountRepository
from src.shared.domain.models import Bank, BankAccount


class BankAccountSyncService:
    """
    Syncs bank account data between snapshot and entities.

    Matching strategy:
    - bank_code + agency_number + account_number
    - If match found: update existing
    - If no match: create new
    - Existing not in snapshot: deactivate (is_active=False)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bank_account_repository = BankAccountRepository(session)

    async def sync_bank_accounts(
        self,
        professional_id: UUID,
        organization_id: UUID,
        bank_accounts_data: list[BankAccountInput],
        updated_by: UUID,
    ) -> list[BankAccount]:
        """Sync bank accounts with snapshot data."""
        existing_accounts = await self._get_existing_accounts(professional_id)

        existing_by_key: dict[tuple[UUID, str, str], BankAccount] = {}
        for account in existing_accounts:
            key = (account.bank_id, account.agency, account.account_number)
            existing_by_key[key] = account

        matched_ids: set[UUID] = set()
        result: list[BankAccount] = []

        for account_data in bank_accounts_data:
            bank = await self._get_bank_by_code(account_data.bank_code)
            if bank is None:
                raise BankNotFoundError(bank_code=account_data.bank_code)

            key = (bank.id, account_data.agency_number, account_data.account_number)
            existing = existing_by_key.get(key)

            if existing:
                matched_ids.add(existing.id)
                updated = await self._update_account(existing, account_data, updated_by)
                result.append(updated)
            else:
                created = await self._create_account(
                    professional_id, bank, account_data, updated_by
                )
                result.append(created)

        # Deactivate accounts not in snapshot
        ids_to_deactivate = [
            account.id for account in existing_accounts if account.id not in matched_ids
        ]
        await self.bank_account_repository.soft_delete_many(ids_to_deactivate)

        await self.session.flush()
        return result

    async def _get_existing_accounts(self, professional_id: UUID) -> list[BankAccount]:
        base_query = select(BankAccount).where(
            BankAccount.organization_professional_id == professional_id
        )
        paginated = await self.bank_account_repository.list(
            limit=100,
            offset=0,
            base_query=base_query,
        )
        return paginated.items

    async def _get_bank_by_code(self, bank_code: str) -> Bank | None:
        result = await self.session.execute(select(Bank).where(Bank.code == bank_code))
        return result.scalar_one_or_none()

    async def _create_account(
        self,
        professional_id: UUID,
        bank: Bank,
        data: BankAccountInput,
        updated_by: UUID,
    ) -> BankAccount:
        account = BankAccount(
            bank_id=bank.id,
            organization_professional_id=professional_id,
            agency=data.agency_number,
            agency_digit=data.agency_digit,
            account_number=data.account_number,
            account_digit=data.account_digit,
            holder_name=data.account_holder_name,
            holder_document=str(data.account_holder_document),
            pix_key_type=data.pix_key_type,
            pix_key=data.pix_key,
            is_primary=data.is_primary,
            is_active=True,
            created_by=updated_by,
            updated_by=updated_by,
        )
        self.session.add(account)
        await self.session.flush()
        return account

    async def _update_account(
        self,
        account: BankAccount,
        data: BankAccountInput,
        updated_by: UUID,
    ) -> BankAccount:
        account.agency_digit = data.agency_digit
        account.account_digit = data.account_digit
        account.holder_name = data.account_holder_name
        account.holder_document = str(data.account_holder_document)
        account.pix_key_type = data.pix_key_type
        account.pix_key = data.pix_key
        account.is_primary = data.is_primary
        account.is_active = True
        account.updated_by = updated_by
        account.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        return account
