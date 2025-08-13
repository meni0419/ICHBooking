# Слой domain: сущности предметной области
# src/accommodations/domain/entities.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .value_objects import Location, Price, RoomsCount, HousingType


@dataclass
class Accommodation:
    """
    Доменная сущность объявления.
    Идентификатор может быть None до сохранения.
    """
    id: Optional[int]
    owner_id: int
    title: str
    description: str
    location: Location
    price: Price
    rooms: RoomsCount
    housing_type: HousingType
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def rename(self, new_title: str) -> None:
        if not new_title or len(new_title.strip()) < 3:
            raise ValueError("Title must be at least 3 chars")
        self.title = new_title.strip()

    def change_description(self, new_description: str) -> None:
        if not new_description or len(new_description.strip()) < 10:
            raise ValueError("Description must be at least 10 chars")
        self.description = new_description.strip()

    def set_price(self, new_price: Price) -> None:
        self.price = new_price

    def set_rooms(self, new_rooms: RoomsCount) -> None:
        self.rooms = new_rooms

    def set_housing_type(self, new_type: HousingType) -> None:
        self.housing_type = new_type

    def toggle_active(self, value: Optional[bool] = None) -> None:
        """Если value не задан — переключаем; иначе выставляем явно."""
        if value is None:
            self.is_active = not self.is_active
        else:
            self.is_active = bool(value)
