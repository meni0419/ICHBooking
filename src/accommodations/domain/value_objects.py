# Слой domain: Value Objects (неизменяемые)
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique


@unique
class HousingType(Enum):
    APARTMENT = "apartment"  # квартира
    HOUSE = "house"  # дом
    STUDIO = "studio"  # студия
    ROOM = "room"  # комната
    OTHER = "other"  # другое


@dataclass(frozen=True)
class Location:
    """Германия: город/регион (земля), страна фиксирована 'DE'."""
    city: str
    region: str
    country: str = "DE"

    def __post_init__(self):
        if not self.city or len(self.city.strip()) < 2:
            raise ValueError("City must be at least 2 chars")
        if not self.region or len(self.region.strip()) < 2:
            raise ValueError("Region must be at least 2 chars")
        if self.country != "DE":
            raise ValueError("Country must be 'DE' for this project")


@dataclass(frozen=True)
class Price:
    """Цена в евро-центах (minor units), чтобы избежать ошибок с float."""
    amount_cents: int

    def __post_init__(self):
        if self.amount_cents <= 0:
            raise ValueError("Price must be > 0 cents")

    @classmethod
    def from_euros(cls, euros: float) -> "Price":
        cents = int(round(euros * 100))
        return cls(amount_cents=cents)

    def as_euros(self) -> float:
        return self.amount_cents / 100.0


@dataclass(frozen=True)
class RoomsCount:
    """Количество комнат (целое положительное)."""
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("RoomsCount must be > 0")
        if self.value > 100:
            raise ValueError("RoomsCount is unrealistically high")
