from __future__ import annotations

from src.shared.errors import ApplicationError
from src.accommodations.application.commands import DeleteAccommodationCommand
from src.accommodations.domain.repository_interfaces import IAccommodationRepository


class DeleteAccommodationUseCase:
    def __init__(self, repo: IAccommodationRepository):
        self._repo = repo

    def execute(self, cmd: DeleteAccommodationCommand) -> None:
        acc = self._repo.get_by_id(cmd.id)
        if not acc:
            raise ApplicationError("Accommodation not found")
        if acc.owner_id != cmd.owner_id:
            raise ApplicationError("Not owner of the accommodation")

        self._repo.delete(cmd.id, owner_id=cmd.owner_id)