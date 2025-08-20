from __future__ import annotations

from src.accommodations.domain.dtos import AccommodationDTO
from src.accommodations.domain.entities import Accommodation


def to_dto(acc: Accommodation) -> AccommodationDTO:
    return AccommodationDTO(
        id=acc.id or 0,
        owner_id=acc.owner_id,
        title=acc.title,
        description=acc.description,
        city=acc.location.city,
        region=acc.location.region,
        country=acc.location.country,
        price_eur=acc.price.as_euros(),
        rooms=acc.rooms.value,
        housing_type=acc.housing_type,
        is_active=acc.is_active,
        impressions_count=acc.impressions_count,
        views_count=acc.views_count,
        reviews_count=acc.reviews_count,
        average_rating=acc.average_rating,
    )
