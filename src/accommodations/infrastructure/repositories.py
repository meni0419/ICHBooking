# Слой infrastructure: реализации репозиториев (Django ORM) адаптеры для domain.repository_interfaces
from __future__ import annotations

from typing import Iterable, Optional

from django.contrib.auth import get_user_model

from src.accommodations.domain.entities import Accommodation as AccDomain
from src.accommodations.domain.repository_interfaces import IAccommodationRepository
from src.accommodations.domain.value_objects import Location, Price, RoomsCount, HousingType
from src.accommodations.infrastructure.orm.models import Accommodation as AccORM

User = get_user_model()


def _to_domain(obj: AccORM) -> AccDomain:
    return AccDomain(
        id=obj.id,
        owner_id=obj.owner_id,
        title=obj.title,
        description=obj.description,
        location=Location(city=obj.city, region=obj.region, country=obj.country),
        price=Price(amount_cents=obj.price_cents),
        rooms=RoomsCount(obj.rooms),
        housing_type=HousingType(obj.housing_type),
        is_active=obj.is_active,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def _apply_domain(acc: AccDomain, obj: AccORM) -> AccORM:
    obj.title = acc.title
    obj.description = acc.description
    obj.city = acc.location.city
    obj.region = acc.location.region
    obj.country = acc.location.country
    obj.price_cents = acc.price.amount_cents
    obj.rooms = acc.rooms.value
    obj.housing_type = acc.housing_type.value
    obj.is_active = acc.is_active
    return obj


class DjangoAccommodationRepository(IAccommodationRepository):
    def get_by_id(self, acc_id: int) -> Optional[AccDomain]:
        try:
            return _to_domain(AccORM.objects.get(pk=acc_id))
        except AccORM.DoesNotExist:
            return None

    def list_by_owner(self, owner_id: int, active_only: bool = False) -> list[AccDomain]:
        qs = AccORM.objects.filter(owner_id=owner_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [_to_domain(o) for o in qs.order_by("-created_at")]

    def search_ids(self, ids: Iterable[int]) -> list[AccDomain]:
        qs = AccORM.objects.filter(id__in=list(ids))
        return [_to_domain(o) for o in qs]

    def create(self, acc: AccDomain) -> AccDomain:
        obj = AccORM(
            owner_id=acc.owner_id,
        )
        obj = _apply_domain(acc, obj)
        obj.save()
        return _to_domain(obj)

    def update(self, acc: AccDomain) -> AccDomain:
        obj = AccORM.objects.get(pk=acc.id)
        # Дополнительно можно убедиться, что owner_id не меняли
        obj = _apply_domain(acc, obj)
        obj.save()
        return _to_domain(obj)

    def delete(self, acc_id: int, owner_id: Optional[int] = None) -> None:
        qs = AccORM.objects.filter(pk=acc_id)
        if owner_id is not None:
            qs = qs.filter(owner_id=owner_id)
        qs.delete()