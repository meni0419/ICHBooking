# src/users/application/ports.py
from __future__ import annotations

from typing import Protocol

from src.users.domain.entities import UserEntity


class IAuthProvider(Protocol):
    """
    Порт для операций, связанных с аутентификацией/паролями.
    Реализация в infrastructure будет создавать пользователя и устанавливать пароль безопасно.
    """
    def create_user_with_password(self, user: UserEntity, password: str) -> UserEntity: ...