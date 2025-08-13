# Слой domain: DTO для обмена данными между слоями (без зависимостей от Django)
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

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