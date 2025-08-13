from __future__ import annotations

from src.shared.errors import ApplicationError
from src.accommodations.application.queries import GetAccommodationByIdQuery
from src.accommodations.domain.dtos import AccommodationDTO
from src.accommodations.application.mappers import to_dto
from src.accommodations.domain.repository_interfaces import IAccommodationRepository


class GetAccommodationByIdUseCase:
    def __init__(self, repo: IAccommodationRepository):
        self._repo = repo

    def execute(self, q: GetAccommodationByIdQuery) -> AccommodationDTO:
        acc = self._repo.get_by_id(q.id)
        if not acc:
            raise ApplicationError("Accommodation not found")
        return to_dto(acc)
