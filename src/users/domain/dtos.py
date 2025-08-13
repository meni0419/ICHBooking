# Слой domain: DTO для обмена данными между слоями (без зависимостей от Django)
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set

from .entities import UserRole
from .value_objects import Email


@dataclass
class UserDTO:
    """DTO для обмена данными о пользователе между слоями."""
    id: int
    name: str
    email: str
    is_active: bool
    roles: Set[UserRole]


@dataclass
class CreateUserDTO:
    """
    DTO для создания пользователя на уровне домена.
    Пароль в домене не хэшируем — это задача infrastructure;
    сюда можно передавать уже хеш (опционально), если понадобится.
    """
    name: str
    email: Email
    password_plain: Optional[str] = None  # может быть None, если создание идёт через соц. провайдера и т.п.
