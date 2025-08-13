# Слой infrastructure: реализации репозиториев (Django ORM) адаптеры для domain.repository_interfaces
from __future__ import annotations

from typing import Iterable, Optional

from django.contrib.auth import get_user_model

from src.users.domain.entities import UserEntity, UserRole
from src.users.domain.repository_interfaces import IUserRepository
from src.users.domain.value_objects import Email

UserORM = get_user_model()


def _roles_to_domain(role_names: list[str]) -> set[UserRole]:
    out: set[UserRole] = set()
    for r in role_names:
        try:
            out.add(UserRole(r))
        except ValueError:
            continue
    return out


def _roles_to_orm(roles: set[UserRole]) -> list[str]:
    return [r.value for r in roles]


def _to_domain(obj: UserORM) -> UserEntity:
    return UserEntity(
        id=obj.id,
        name=obj.name or "",
        email=Email(obj.email),
        is_active=obj.is_active,
        roles=_roles_to_domain(obj.roles or []),
        created_at=None,
        updated_at=None,
    )


class DjangoUserRepository(IUserRepository):
    """Django ORM-реализация контракта IUserRepository."""

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        try:
            obj = UserORM.objects.get(pk=user_id)
            return _to_domain(obj)
        except UserORM.DoesNotExist:
            return None

    def get_by_email(self, email: Email) -> Optional[UserEntity]:
        try:
            obj = UserORM.objects.get(email=str(email))
            return _to_domain(obj)
        except UserORM.DoesNotExist:
            return None

    def exists_by_email(self, email: Email) -> bool:
        return UserORM.objects.filter(email=str(email)).exists()

    def list_by_ids(self, ids: Iterable[int]) -> list[UserEntity]:
        objects = UserORM.objects.filter(id__in=list(ids))
        return [_to_domain(o) for o in objects]

    def create(self, user: UserEntity) -> UserEntity:
        obj = UserORM.objects.create(
            email=str(user.email),
            name=user.name,
            is_active=user.is_active,
            roles=_roles_to_orm(user.roles),
        )
        return _to_domain(obj)

    def update(self, user: UserEntity) -> UserEntity:
        obj = UserORM.objects.get(pk=user.id)
        obj.name = user.name
        obj.is_active = user.is_active
        obj.roles = _roles_to_orm(user.roles)
        obj.save(update_fields=["name", "is_active", "roles"])
        return _to_domain(obj)
