# Слой domain: Value Objects (неизменяемые)
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rating:
    """Оценка по шкале 1..5."""
    value: int

    def __post_init__(self):
        if not 1 <= self.value <= 5:
            raise ValueError("Rating value must be in range 1..5")
