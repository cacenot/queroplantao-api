"""OrganizationScreeningSettings repository for database operations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.screening.domain.models import OrganizationScreeningSettings
from src.shared.infrastructure.repositories import (
    BaseRepository,
    OrganizationScopeMixin,
    ScopePolicy,
)


class OrganizationScreeningSettingsRepository(
    OrganizationScopeMixin[OrganizationScreeningSettings],
    BaseRepository[OrganizationScreeningSettings],
):
    """
    Repository for OrganizationScreeningSettings model.

    Provides CRUD operations for organization screening configuration.
    1:1 relationship with Organization - one settings per org.
    """

    model = OrganizationScreeningSettings
    default_scope_policy = "ORGANIZATION_ONLY"

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query_for_organization(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ):
        org_ids = self._get_effective_org_ids(
            organization_id=organization_id,
            family_org_ids=family_org_ids or (),
            scope_policy=scope_policy,
        )
        base_query = super().get_query()  # type: ignore[misc]
        return self._apply_org_scope(base_query, org_ids)

    async def get_by_organization_id(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ) -> OrganizationScreeningSettings | None:
        """
        Get settings by organization ID.

        Args:
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Settings if found, None otherwise.
        """
        query = self._base_query_for_organization(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        ).where(OrganizationScreeningSettings.organization_id == organization_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_default(
        self,
        organization_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ) -> OrganizationScreeningSettings:
        """
        Get existing settings or create with defaults.

        Args:
            organization_id: The organization UUID.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Settings instance (existing or newly created).
        """
        existing = await self.get_by_organization_id(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        )
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
        family_org_ids: list[UUID] | tuple[UUID, ...] | None,
        scope_policy: ScopePolicy | None = None,
    ) -> OrganizationScreeningSettings | None:
        """
        Update settings for an organization.

        Args:
            organization_id: The organization UUID.
            update_data: Dictionary with fields to update.
            family_org_ids: List of family org IDs (required for FAMILY scope).
            scope_policy: Scope policy to apply. Uses default if None.

        Returns:
            Updated settings or None if not found.
        """
        settings = await self.get_by_organization_id(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            scope_policy=scope_policy,
        )
        if not settings:
            return None

        for field, value in update_data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)

        await self.session.flush()
        await self.session.refresh(settings)
        return settings
