from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model

from src.accommodations.infrastructure.orm.models import Accommodation as AccORM


User = get_user_model()


def create_user(email: str, password: Optional[str] = None, name: str = "Test User"):
    """
    Простая фабрика пользователя. Пароль опционален (для force_authenticate не нужен).
    """
    user = User.objects.create_user(email=email, password=password or None)
    # Пытаемся заполнить имя, если поле есть
    if hasattr(user, "name"):
        user.name = name
        user.save(update_fields=["name"])
    return user


def create_accommodation(
    *,
    owner_id: int,
    title: str = "Cozy flat",
    description: str = "Nice place to stay",
    city: str = "Berlin",
    region: str = "Berlin",
    country: str = "DE",
    price_cents: int = 10000,
    rooms: int = 2,
    housing_type: str = "apartment",
    is_active: bool = True,
) -> AccORM:
    return AccORM.objects.create(
        owner_id=owner_id,
        title=title,
        description=description,
        city=city,
        region=region,
        country=country,
        price_cents=price_cents,
        rooms=rooms,
        housing_type=housing_type,
        is_active=is_active,
    )