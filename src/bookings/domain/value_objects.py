# Слой domain: Value Objects (неизменяемые)
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class StayPeriod:
    """Интервал проживания [start_date, end_date), end > start."""
    start_date: date
    end_date: date

    def __post_init__(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")

    def overlaps(self, other: "StayPeriod") -> bool:
        """Пересечение полуинтервалов [a,b) и [c,d) => not (b <= c or d <= a)."""
        return not (self.end_date <= other.start_date or other.end_date <= self.start_date)

    def contains(self, d: date) -> bool:
        return self.start_date <= d < self.end_date

    def days(self) -> int:
        return (self.end_date - self.start_date).days
