# Слой domain: сущности предметной области
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, unique
from typing import Optional, Set

from .value_objects import Email


@unique
class UserRole(Enum):
    """Доменные роли. Админку оставляем инфраструктуре (is_staff/superuser)."""
    HOST = "host"    # арендодатель
    GUEST = "guest"  # арендатор


@dataclass
class UserEntity:
    """
    Чистая доменная модель пользователя.
    Идентификатор может быть None для несохранённых сущностей.
    """
    id: Optional[int]
    name: str
    email: Email
    is_active: bool = True
    roles: Set[UserRole] = field(default_factory=set)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def has_role(self, role: UserRole) -> bool:
        return role in self.roles

    def add_role(self, role: UserRole) -> None:
        self.roles.add(role)

    def remove_role(self, role: UserRole) -> None:
        self.roles.discard(role)
