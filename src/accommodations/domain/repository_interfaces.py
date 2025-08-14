# Слой domain: контракты репозиториев
from __future__ import annotations

from typing import Iterable, Optional, Protocol, runtime_checkable, Tuple

from .entities import Accommodation
from .dtos import SearchQueryDTO


@runtime_checkable
class IAccommodationRepository(Protocol):
    """Контракт репозитория для объявлений."""

    def get_by_id(self, acc_id: int) -> Optional[Accommodation]: ...

    def list_by_owner(self, owner_id: int, active_only: bool = False) -> list[Accommodation]: ...

    def search_ids(self, ids: Iterable[int]) -> list[Accommodation]: ...

    def create(self, acc: Accommodation) -> Accommodation: ...

    def update(self, acc: Accommodation) -> Accommodation: ...

    def delete(self, acc_id: int, owner_id: Optional[int] = None) -> None: ...

    def search(self, q: SearchQueryDTO) -> Tuple[list[Accommodation], int]: ...
