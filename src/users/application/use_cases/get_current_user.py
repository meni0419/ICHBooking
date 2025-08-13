# src/users/application/use_cases/get_current_user.py
from __future__ import annotations

from src.shared.errors import ApplicationError
from src.users.application.queries import GetCurrentUserQuery
from src.users.domain.dtos import UserDTO
from src.users.domain.repository_interfaces import IUserRepository


class GetCurrentUserUseCase:
    """Вернуть данные текущего пользователя по user_id."""
    def __init__(self, users: IUserRepository):
        self._users = users

    def execute(self, q: GetCurrentUserQuery) -> UserDTO:
        user = self._users.get_by_id(q.user_id)
        if not user:
            raise ApplicationError("User not found")
        return UserDTO(
            id=user.id,  # type: ignore[arg-type]
            name=user.name,
            email=str(user.email),
            is_active=user.is_active,
            roles=user.roles,
        )