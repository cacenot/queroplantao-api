"""Use case for updating current user's profile."""

from uuid import UUID

from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import ConflictError, NotFoundError
from src.app.i18n import AuthMessages, get_message
from src.modules.users.domain.schemas import UserMeResponse, UserMeUpdate
from src.modules.users.infrastructure.repositories.user_repository import UserRepository
from src.modules.users.use_cases.get_me_use_case import GetMeUseCase


class UpdateMeUseCase:
    """
    Use case for updating current user's profile.

    Supports PATCH semantics - only fields explicitly provided will be updated.
    Email is not editable through this endpoint as it requires Firebase sync.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = UserRepository(session)

    async def execute(
        self,
        user_id: UUID,
        data: UserMeUpdate,
    ) -> UserMeResponse:
        """
        Update current user's profile.

        Args:
            user_id: The authenticated user's UUID.
            data: Update data (PATCH semantics - only provided fields are updated).

        Returns:
            UserMeResponse with complete updated user data.

        Raises:
            NotFoundError: If user not found.
            ConflictError: If CPF is already in use by another user.
        """
        # 1. Get existing user
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(resource="User", identifier=str(user_id))

        # 2. Get only fields that were explicitly set (PATCH semantics)
        update_data = data.model_dump(exclude_unset=True)

        # 3. Validate CPF uniqueness if being changed
        if "cpf" in update_data:
            new_cpf = update_data["cpf"]
            if new_cpf is not None and new_cpf != user.cpf:
                if await self.repository.exists_by_cpf(new_cpf, exclude_id=user_id):
                    raise ConflictError(
                        message=get_message(AuthMessages.CPF_ALREADY_IN_USE)
                    )

        # 4. Apply updates
        for field, value in update_data.items():
            # Convert HttpUrl to string for database storage
            if isinstance(value, HttpUrl):
                value = str(value)
            setattr(user, field, value)

        # 5. Set updated_by (from TrackingMixin)
        user.updated_by = user_id

        # 6. Save changes
        await self.repository.update(user)

        # 7. Return complete user response using GetMeUseCase logic
        get_me = GetMeUseCase(self.session)
        return await get_me.execute(user_id)
