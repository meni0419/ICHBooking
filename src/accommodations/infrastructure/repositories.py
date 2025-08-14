# Слой infrastructure: реализации репозиториев (Django ORM) адаптеры для domain.repository_interfaces
from __future__ import annotations

from typing import Iterable, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

from src.accommodations.domain.entities import Accommodation as AccDomain
from src.accommodations.domain.repository_interfaces import IAccommodationRepository
from src.accommodations.domain.value_objects import Location, Price, RoomsCount, HousingType
from src.accommodations.domain.dtos import SearchQueryDTO, SearchSort
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

    def search(self, q: SearchQueryDTO) -> Tuple[list[AccDomain], int]:
        qs: QuerySet[AccORM] = AccORM.objects.all()

        # only_active
        if q.only_active:
            qs = qs.filter(is_active=True)

        # keyword по title/description
        if q.keyword:
            kw = q.keyword
            qs = qs.filter(Q(title__icontains=kw) | Q(description__icontains=kw))

        # Локация: по city/region (case-insensitive, частичное совпадение)
        if q.city:
            qs = qs.filter(city__icontains=q.city)
        if q.region:
            qs = qs.filter(region__icontains=q.region)

        # Цена (евро -> центы)
        if q.price_min is not None:
            qs = qs.filter(price_cents__gte=int(round(q.price_min * 100)))
        if q.price_max is not None:
            qs = qs.filter(price_cents__lte=int(round(q.price_max * 100)))

        # Комнаты
        if q.rooms_min is not None:
            qs = qs.filter(rooms__gte=q.rooms_min)
        if q.rooms_max is not None:
            qs = qs.filter(rooms__lte=q.rooms_max)

        # Типы жилья
        if q.housing_types:
            qs = qs.filter(housing_type__in=[t.value for t in q.housing_types])

        # Сортировка
        if q.sort == SearchSort.PRICE_ASC:
            qs = qs.order_by("price_cents", "-id")
        elif q.sort == SearchSort.PRICE_DESC:
            qs = qs.order_by("-price_cents", "-id")
        elif q.sort == SearchSort.CREATED_AT_ASC:
            qs = qs.order_by("created_at", "id")
        else:
            # CREATED_AT_DESC (по умолчанию)
            qs = qs.order_by("-created_at", "-id")

        # Подсчёт total до пагинации
        total = qs.count()

        # Пагинация
        page = max(1, q.page)
        page_size = max(1, q.page_size)
        offset = (page - 1) * page_size
        items_qs = qs[offset: offset + page_size]

        return ([_to_domain(o) for o in items_qs], total)
