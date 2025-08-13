# Слой domain: доменные сервисы (чистые функции/классы без инфраструктуры)
from __future__ import annotations

from .entities import Accommodation
from .value_objects import Location, Price, RoomsCount, HousingType
from .dtos import SearchQueryDTO, SearchSort


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


def normalize_search_query(q: SearchQueryDTO) -> SearchQueryDTO:
    """
    Нормализует/валидирует параметры поиска:
    - keyword -> trimmed/lower (для простого поиска, конкретная логика — на application/infrastructure)
    - перестановка Min/Max при ошибочном порядке
    - клампинг отрицательных значений
    - дефолты для пагинации и сортировки
    """
    keyword = (q.keyword or "").strip()
    keyword = keyword if keyword else None

    price_min = q.price_min
    price_max = q.price_max
    if price_min is not None and price_min < 0:
        price_min = 0.0
    if price_max is not None and price_max < 0:
        price_max = 0.0
    if price_min is not None and price_max is not None and price_min > price_max:
        price_min, price_max = price_max, price_min

    rooms_min = q.rooms_min
    rooms_max = q.rooms_max
    if rooms_min is not None and rooms_min < 0:
        rooms_min = 0
    if rooms_max is not None and rooms_max < 0:
        rooms_max = 0
    if rooms_min is not None and rooms_max is not None and rooms_min > rooms_max:
        rooms_min, rooms_max = rooms_max, rooms_min

    # Нормализация housing_types: уникальные, валидные
    housing_types = list(dict.fromkeys(q.housing_types or []))  # preserve order + unique

    # Пагинация: простые дефолты/границы
    page = q.page if q.page and q.page > 0 else 1
    page_size = q.page_size if q.page_size and q.page_size > 0 else 20
    if page_size > 100:
        page_size = 100

    sort = q.sort if isinstance(q.sort, SearchSort) else SearchSort.CREATED_AT_DESC

    return SearchQueryDTO(
        keyword=keyword,
        price_min=price_min,
        price_max=price_max,
        city=(q.city or "").strip() or None,
        region=(q.region or "").strip() or None,
        rooms_min=rooms_min,
        rooms_max=rooms_max,
        housing_types=housing_types,
        only_active=bool(q.only_active),
        sort=sort,
        page=page,
        page_size=page_size,
    )
