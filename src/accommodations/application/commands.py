# Слой application: команды (модифицирующие сценарии)
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateAccommodationCommand:
    owner_id: int
    title: str
    description: str
    city: str
    region: str
    price_eur: float
    rooms: int
    housing_type: str  # "apartment" | "house" | "studio" | "room" | "other"
    is_active: Optional[bool] = True


@dataclass(frozen=True)
class UpdateAccommodationCommand:
    id: int
    owner_id: int  # владелец, совершающий действие (проверка владения на уровне интерфейсов/репозитория)
    title: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    price_eur: Optional[float] = None
    rooms: Optional[int] = None
    housing_type: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass(frozen=True)
class DeleteAccommodationCommand:
    id: int
    owner_id: int


@dataclass(frozen=True)
class ToggleAvailabilityCommand:
    id: int
    owner_id: int
    value: Optional[bool] = None  # None = переключить; True/False = установить явно
