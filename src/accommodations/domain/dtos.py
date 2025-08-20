# Слой domain: DTO для обмена данными между слоями (без зависимостей от Django)
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Optional, Sequence

from .value_objects import HousingType


@dataclass
class AccommodationDTO:
    """DTO для чтения/отдачи наружу (например, в интерфейсах)."""
    id: int
    owner_id: int
    title: str
    description: str
    city: str
    region: str
    country: str
    price_eur: float
    rooms: int
    housing_type: HousingType
    is_active: bool
    impressions_count: int
    views_count: int
    reviews_count: int
    average_rating: float
    reviews_count: int
    average_rating: float


@dataclass
class CreateAccommodationDTO:
    """DTO для создания объявления (используется на границе application)."""
    owner_id: int
    title: str
    description: str
    city: str
    region: str
    price_eur: float
    rooms: int
    housing_type: HousingType
    is_active: Optional[bool] = True


@dataclass
class UpdateAccommodationDTO:
    """DTO для обновления объявления (частичное или полное — решит use-case)."""
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    price_eur: Optional[float] = None
    rooms: Optional[int] = None
    housing_type: Optional[HousingType] = None
    is_active: Optional[bool] = None


@unique
class SearchSort(Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    CREATED_AT_ASC = "created_at_asc"
    CREATED_AT_DESC = "created_at_desc"
    POPULAR = "popular"
    VIEWS = "views"
    RATING_DESC = "rating_desc"
    RATING_ASC = "rating_asc"
    REVIEWS_DESC = "reviews_desc"
    REVIEWS_ASC = "reviews_asc"


@dataclass
class SearchQueryDTO:
    """
    Параметры поиска:
    - keyword: поиск по title/description
    - price_min/max: в евро
    - city/region: фильтр локации (DE фиксируется в домене)
    - rooms_min/max: диапазон комнат
    - housing_types: список HousingType для фильтра
    - only_active: брать только активные объявления
    - sort: вариант сортировки
    - page/page_size: пагинация (на усмотрение application-слоя)
    """
    keyword: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    city: Optional[str] = None
    region: Optional[str] = None
    rooms_min: Optional[int] = None
    rooms_max: Optional[int] = None
    housing_types: Sequence[HousingType] = field(default_factory=list)
    only_active: bool = True
    sort: SearchSort = SearchSort.CREATED_AT_DESC
    page: int = 1
    page_size: int = 20
