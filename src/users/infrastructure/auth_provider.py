from __future__ import annotations

from django.contrib.auth import get_user_model

from src.users.application.ports import IAuthProvider
from src.users.domain.entities import UserEntity
from src.users.infrastructure.repositories import _roles_to_orm

UserORM = get_user_model()


class DjangoAuthProvider(IAuthProvider):
    def create_user_with_password(self, user: UserEntity, password: str) -> UserEntity:
        obj = UserORM.objects.create_user(
            email=str(user.email),
            password=password,
            name=user.name,
            is_active=user.is_active,
            roles=_roles_to_orm(user.roles),
        )
        # Возвращаем доменную сущность (если нужно — через общий mapper)
        from src.users.infrastructure.repositories import _to_domain
        return _to_domain(obj)