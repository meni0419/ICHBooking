# Слой application: команды (модифицирующие сценарии)
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from src.users.domain.entities import UserRole
from src.users.domain.value_objects import Email


@dataclass(frozen=True)
class RegisterUserCommand:
    name: str
    email: Email
    password: str
    password_confirm: str
    # Какую роль выдать по умолчанию при регистрации (можно null -> guest по умолчанию)
    initial_roles: Optional[Iterable[UserRole]] = None


@dataclass(frozen=True)
class AddRoleCommand:
    user_id: int
    role: UserRole


@dataclass(frozen=True)
class RemoveRoleCommand:
    user_id: int
    role: UserRole
