from __future__ import annotations

from src.shared.errors import ApplicationError
from src.accommodations.application.commands import CreateAccommodationCommand
from src.accommodations.domain.dtos import AccommodationDTO
from src.accommodations.application.mappers import to_dto
from src.accommodations.domain.repository_interfaces import IAccommodationRepository
from src.accommodations.domain.services import create_accommodation
from src.accommodations.domain.value_objects import Location, Price, RoomsCount, HousingType


class CreateAccommodationUseCase:
    def __init__(self, repo: IAccommodationRepository):
        self._repo = repo

    def execute(self, cmd: CreateAccommodationCommand) -> AccommodationDTO:
        try:
            location = Location(city=cmd.city, region=cmd.region)
            price = Price.from_euros(cmd.price_eur)
            rooms = RoomsCount(cmd.rooms)
            try:
                htype = HousingType(cmd.housing_type)
            except ValueError:
                raise ApplicationError("Unsupported housing_type")

            entity = create_accommodation(
                owner_id=cmd.owner_id,
                title=cmd.title,
                description=cmd.description,
                location=location,
                price=price,
                rooms=rooms,
                housing_type=htype,
                is_active=bool(cmd.is_active),
            )
            created = self._repo.create(entity)
            return to_dto(created)
        except ApplicationError:
            raise
        except Exception as ex:
            raise ApplicationError(str(ex))