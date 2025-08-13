# Слой application: запросы (чтение)
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetAccommodationByIdQuery:
    id: int
