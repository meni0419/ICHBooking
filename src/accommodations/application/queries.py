# Слой application: запросы (чтение)
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

from src.accommodations.domain.value_objects import HousingType
from src.accommodations.domain.dtos import SearchSort


@dataclass(frozen=True)
class GetAccommodationByIdQuery:
    id: int

@dataclass(frozen=True)
class SearchAccommodationsQuery:
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

