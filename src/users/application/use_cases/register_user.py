from __future__ import annotations

from typing import Iterable

from src.shared.errors import ApplicationError
from src.users.application.commands import RegisterUserCommand
from src.users.application.ports import IAuthProvider
from src.users.domain.dtos import UserDTO
from src.users.domain.entities import UserEntity, UserRole
from src.users.domain.repository_interfaces import IUserRepository
from src.users.domain.services import assign_role


class RegisterUserUseCase:
    """
    Use-case регистрации пользователя.
    Валидация паролей (password == password_confirm), проверка уникальности email.
    Создание пользователя делегируется IAuthProvider, чтобы безопасно установить пароль.
    """
    def __init__(self, users: IUserRepository, auth: IAuthProvider):
        self._users = users
        self._auth = auth

    def execute(self, cmd: RegisterUserCommand) -> UserDTO:
        if cmd.password != cmd.password_confirm:
            raise ApplicationError("Passwords do not match")

        if self._users.exists_by_email(cmd.email):
            raise ApplicationError("User with this email already exists")

        roles: Iterable[UserRole] = cmd.initial_roles or [UserRole.GUEST]

        entity = UserEntity(
            id=None,
            name=cmd.name,
            email=cmd.email,
            is_active=True,
            roles=set(),
        )
        for r in roles:
            assign_role(entity, r)

        # Создание и установка пароля — через инфраструктурный провайдер
        created = self._auth.create_user_with_password(entity, cmd.password)

        return UserDTO(
            id=created.id,  # type: ignore[arg-type]
            name=created.name,
            email=str(created.email),
            is_active=created.is_active,
            roles=created.roles,
        )