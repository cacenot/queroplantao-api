"""BankAccount repository for database operations."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models import BankAccount
from src.shared.infrastructure.repositories import BaseRepository


class BankAccountRepository(BaseRepository[BankAccount]):
    """
    Repository for BankAccount model.

    Provides CRUD operations and helper methods for professional-owned
    bank accounts.
    """

    model = BankAccount

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_professional(
        self,
        professional_id: UUID,
    ) -> Select[tuple[BankAccount]]:
        """
        Get base query filtered by professional.

        Args:
            professional_id: The organization professional UUID.

        Returns:
            Query filtered by professional.
        """
        return select(BankAccount).where(
            BankAccount.organization_professional_id == professional_id
        )

    async def get_by_id_for_professional(
        self,
        id: UUID,
        professional_id: UUID,
    ) -> BankAccount | None:
        """
        Get bank account by ID for a professional.

        Args:
            id: The bank account UUID.
            professional_id: The organization professional UUID.

        Returns:
            Bank account if found, None otherwise.
        """
        result = await self.session.execute(
            self._base_query_for_professional(professional_id).where(
                BankAccount.id == id
            )
        )
        return result.scalar_one_or_none()

    async def create_many(self, bank_accounts: list[BankAccount]) -> list[BankAccount]:
        """Create multiple bank accounts in bulk."""
        self.session.add_all(bank_accounts)
        await self.session.flush()
        return bank_accounts

    async def soft_delete(self, id: UUID) -> None:
        """Deactivate a bank account by ID (soft delete via is_active)."""
        result = await self.session.execute(
            select(BankAccount).where(BankAccount.id == id)
        )
        bank_account = result.scalar_one_or_none()
        if bank_account:
            bank_account.is_active = False
            await self.session.flush()

    async def soft_delete_many(self, ids: list[UUID]) -> None:
        """Deactivate multiple bank accounts (soft delete via is_active)."""
        if not ids:
            return
        result = await self.session.execute(
            select(BankAccount).where(BankAccount.id.in_(ids))
        )
        bank_accounts = list(result.scalars().all())
        for bank_account in bank_accounts:
            bank_account.is_active = False
        await self.session.flush()
