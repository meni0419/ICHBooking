# Слой domain: доменные сервисы (чистые функции/классы без инфраструктуры)
from __future__ import annotations

from .entities import UserEntity, UserRole


def assign_role(user: UserEntity, role: UserRole) -> None:
    """
    Бизнес-правило: пользователь может иметь одновременно роли HOST и GUEST.
    Админские привилегии — вне домена (через Django is_staff/superuser).
    """
    user.add_role(role)


def revoke_role(user: UserEntity, role: UserRole) -> None:
    """Снять роль с пользователя."""
    user.remove_role(role)


def can_create_accommodation(user: UserEntity) -> bool:
    """Только HOST может создавать объявления."""
    return user.is_active and user.has_role(UserRole.HOST)


def can_manage_own_accommodations(user: UserEntity) -> bool:
    """HOST может управлять собственными объявлениями."""
    return can_create_accommodation(user)


def can_book_accommodation(user: UserEntity) -> bool:
    """GUEST может бронировать."""
    return user.is_active and user.has_role(UserRole.GUEST)
