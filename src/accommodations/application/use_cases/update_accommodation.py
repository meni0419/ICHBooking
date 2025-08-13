from __future__ import annotations

from typing import Optional

from src.shared.errors import ApplicationError
from src.accommodations.application.commands import UpdateAccommodationCommand
from src.accommodations.domain.dtos import AccommodationDTO
from src.accommodations.application.mappers import to_dto
from src.accommodations.domain.repository_interfaces import IAccommodationRepository
from src.accommodations.domain.services import update_accommodation
from src.accommodations.domain.value_objects import Location, Price, RoomsCount, HousingType


class UpdateAccommodationUseCase:
    def __init__(self, repo: IAccommodationRepository):
        self._repo = repo

    def execute(self, cmd: UpdateAccommodationCommand) -> AccommodationDTO:
        acc = self._repo.get_by_id(cmd.id)
        if not acc:
            raise ApplicationError("Accommodation not found")
        if acc.owner_id != cmd.owner_id:
            raise ApplicationError("Not owner of the accommodation")

        def _loc_or_none() -> Optional[Location]:
            if cmd.city is None and cmd.region is None:
                return None
            city = cmd.city if cmd.city is not None else acc.location.city
            region = cmd.region if cmd.region is not None else acc.location.region
            return Location(city=city, region=region)

        location = _loc_or_none()
        price = Price.from_euros(cmd.price_eur) if cmd.price_eur is not None else None
        rooms = RoomsCount(cmd.rooms) if cmd.rooms is not None else None
        htype = None
        if cmd.housing_type is not None:
            try:
                htype = HousingType(cmd.housing_type)
            except ValueError:
                raise ApplicationError("Unsupported housing_type")

        try:
            updated = update_accommodation(
                acc,
                title=cmd.title,
                description=cmd.description,
                location=location,
                price=price,
                rooms=rooms,
                housing_type=htype,
                is_active=cmd.is_active,
            )
            saved = self._repo.update(updated)
            return to_dto(saved)
        except ApplicationError:
            raise
        except Exception as ex:
            raise ApplicationError(str(ex))
