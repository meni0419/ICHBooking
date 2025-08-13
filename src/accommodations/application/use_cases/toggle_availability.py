from __future__ import annotations

from src.shared.errors import ApplicationError
from src.accommodations.application.commands import ToggleAvailabilityCommand
from src.accommodations.domain.dtos import AccommodationDTO
from src.accommodations.application.mappers import to_dto
from src.accommodations.domain.repository_interfaces import IAccommodationRepository


class ToggleAvailabilityUseCase:
    def __init__(self, repo: IAccommodationRepository):
        self._repo = repo

    def execute(self, cmd: ToggleAvailabilityCommand) -> AccommodationDTO:
        acc = self._repo.get_by_id(cmd.id)
        if not acc:
            raise ApplicationError("Accommodation not found")
        if acc.owner_id != cmd.owner_id:
            raise ApplicationError("Not owner of the accommodation")

        acc.toggle_active(cmd.value)
        saved = self._repo.update(acc)
        return to_dto(saved)
