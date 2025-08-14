from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.accommodations.domain.dtos import AccommodationDTO


@dataclass
class SearchPageDTO:
    page: int
    page_size: int
    total: int


@dataclass
class SearchResultDTO:
    items: List[AccommodationDTO]
    page: SearchPageDTO