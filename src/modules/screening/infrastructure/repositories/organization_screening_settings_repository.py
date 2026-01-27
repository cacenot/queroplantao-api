"""OrganizationScreeningSettings repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models import OrganizationScreeningSettings
from src.shared.infrastructure.repositories import BaseRepository


class OrganizationScreeningSettingsRepository(
    BaseRepository[OrganizationScreeningSettings],
):
    """
    Repository for OrganizationScreeningSettings model.

    Provides CRUD operations for organization screening configuration.
    1:1 relationship with Organization - one settings per org.
    """

    model = OrganizationScreeningSettings

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_organization_id(
        self,
        organization_id: UUID,
    ) -> OrganizationScreeningSettings | None:
        """
        Get settings by organization ID.

        Args:
            organization_id: The organization UUID.

        Returns:
            Settings if found, None otherwise.
        """
        query = select(OrganizationScreeningSettings).where(
            OrganizationScreeningSettings.organization_id == organization_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_default(
        self,
        organization_id: UUID,
    ) -> OrganizationScreeningSettings:
        """
        Get existing settings or create with defaults.

        Args:
            organization_id: The organization UUID.

        Returns:
            Settings instance (existing or newly created).
        """
        existing = await self.get_by_organization_id(organization_id)
        if existing:
            return existing

        # Create default settings
        settings = OrganizationScreeningSettings(
            organization_id=organization_id,
        )
        return await self.create(settings)

    async def update_settings(
        self,
        organization_id: UUID,
        update_data: dict,
    ) -> OrganizationScreeningSettings | None:
        """
        Update settings for an organization.

        Args:
            organization_id: The organization UUID.
            update_data: Dictionary with fields to update.

        Returns:
            Updated settings or None if not found.
        """
        settings = await self.get_by_organization_id(organization_id)
        if not settings:
            return None

        for field, value in update_data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)

        await self.session.flush()
        await self.session.refresh(settings)
        return settings
