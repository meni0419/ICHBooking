from __future__ import annotations

from src.shared.errors import ApplicationError
from src.users.application.commands import AddRoleCommand, RemoveRoleCommand
from src.users.domain.dtos import UserDTO
from src.users.domain.entities import UserRole
from src.users.domain.repository_interfaces import IUserRepository
from src.users.domain.services import assign_role, revoke_role


class AddRoleUseCase:
    """Добавить роль пользователю (self-service переключение режимов)."""
    def __init__(self, users: IUserRepository):
        self._users = users

    def execute(self, cmd: AddRoleCommand) -> UserDTO:
        user = self._users.get_by_id(cmd.user_id)
        if not user:
            raise ApplicationError("User not found")

        if cmd.role not in (UserRole.HOST, UserRole.GUEST):
            raise ApplicationError("Unsupported role")

        assign_role(user, cmd.role)
        saved = self._users.update(user)

        return UserDTO(
            id=saved.id,  # type: ignore[arg-type]
            name=saved.name,
            email=str(saved.email),
            is_active=saved.is_active,
            roles=saved.roles,
        )


class RemoveRoleUseCase:
    """Удалить роль у пользователя (например, выключить режим host)."""
    def __init__(self, users: IUserRepository):
        self._users = users

    def execute(self, cmd: RemoveRoleCommand) -> UserDTO:
        user = self._users.get_by_id(cmd.user_id)
        if not user:
            raise ApplicationError("User not found")

        if cmd.role not in (UserRole.HOST, UserRole.GUEST):
            raise ApplicationError("Unsupported role")

        revoke_role(user, cmd.role)
        saved = self._users.update(user)

        return UserDTO(
            id=saved.id,  # type: ignore[arg-type]
            name=saved.name,
            email=str(saved.email),
            is_active=saved.is_active,
            roles=saved.roles,
        )