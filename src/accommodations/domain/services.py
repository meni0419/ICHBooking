# Слой domain: доменные сервисы (чистые функции/классы без инфраструктуры)
from __future__ import annotations

from .entities import Accommodation
from .value_objects import Location, Price, RoomsCount, HousingType


def validate_title(title: str) -> None:
    if not title or len(title.strip()) < 3:
        raise ValueError("Title must be at least 3 chars")


def validate_description(description: str) -> None:
    if not description or len(description.strip()) < 10:
        raise ValueError("Description must be at least 10 chars")


def create_accommodation(
    *,
    owner_id: int,
    title: str,
    description: str,
    location: Location,
    price: Price,
    rooms: RoomsCount,
    housing_type: HousingType,
    is_active: bool = True,
) -> Accommodation:
    """
    Фабричный метод домена — централизует инварианты:
    - валидность title/description
    - корректные VO уже проверены их конструкторами
    """
    validate_title(title)
    validate_description(description)
    return Accommodation(
        id=None,
        owner_id=owner_id,
        title=title.strip(),
        description=description.strip(),
        location=location,
        price=price,
        rooms=rooms,
        housing_type=housing_type,
        is_active=is_active,
    )


def update_accommodation(
    acc: Accommodation,
    *,
    title: str | None = None,
    description: str | None = None,
    location: Location | None = None,
    price: Price | None = None,
    rooms: RoomsCount | None = None,
    housing_type: HousingType | None = None,
    is_active: bool | None = None,
) -> Accommodation:
    """Применяет изменения к сущности с валидацией доменных инвариантов."""
    if title is not None:
        acc.rename(title)
    if description is not None:
        acc.change_description(description)
    if location is not None:
        acc.location = location
    if price is not None:
        acc.set_price(price)
    if rooms is not None:
        acc.set_rooms(rooms)
    if housing_type is not None:
        acc.set_housing_type(housing_type)
    if is_active is not None:
        acc.toggle_active(is_active)
    return acc
