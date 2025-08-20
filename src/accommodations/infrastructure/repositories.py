# Слой infrastructure: реализации репозиториев (Django ORM) адаптеры для domain.repository_interfaces
from __future__ import annotations

from typing import Iterable, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, QuerySet, F, Count

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
        impressions_count=obj.impressions_count,
        views_count=obj.views_count,
        reviews_count=getattr(obj, "reviews_count", 0),
        average_rating=float(getattr(obj, "average_rating", 0) or 0),
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
            qs = AccORM.objects.filter(pk=acc_id)
            return _to_domain(qs.get())
        except AccORM.DoesNotExist:
            return None

    def list_by_owner(self, owner_id: int, active_only: bool = False) -> list[AccDomain]:
        qs = AccORM.objects.filter(owner_id=owner_id)
        if active_only:
            qs = qs.filter(is_active=True)
        qs = qs.order_by("-created_at")
        return [_to_domain(o) for o in qs]

    def search_ids(self, ids: Iterable[int]) -> list[AccDomain]:
        qs = AccORM.objects.filter(id__in=list(ids))
        return [_to_domain(o) for o in qs]

    def create(self, acc: AccDomain) -> AccDomain:
        obj = AccORM(owner_id=acc.owner_id)
        obj = _apply_domain(acc, obj)
        obj.save()
        return _to_domain(AccORM.objects.get(pk=obj.id))

    def update(self, acc: AccDomain) -> AccDomain:
        obj = AccORM.objects.get(pk=acc.id)
        obj = _apply_domain(acc, obj)
        obj.save()
        return _to_domain(AccORM.objects.get(pk=obj.id))

    def delete(self, acc_id: int, owner_id: Optional[int] = None) -> None:
        qs = AccORM.objects.filter(pk=acc_id)
        if owner_id is not None:
            qs = qs.filter(owner_id=owner_id)
        qs.delete()

    def increment_views(self, acc_id: int) -> None:
        AccORM.objects.filter(pk=acc_id).update(views_count=F("views_count") + 1)

    def _apply_sort(self, qs: QuerySet, sort: SearchSort) -> QuerySet:
        # Маппинг сортировок на поля ORM (используем денормализованные поля модели)
        if sort == SearchSort.PRICE_ASC:
            return qs.order_by("price_cents", "-id")
        if sort == SearchSort.PRICE_DESC:
            return qs.order_by("-price_cents", "-id")
        if sort == SearchSort.CREATED_AT_ASC:
            return qs.order_by("created_at", "id")
        if sort == SearchSort.CREATED_AT_DESC:
            return qs.order_by("-created_at", "-id")
        if sort == SearchSort.VIEWS:
            # Сначала по количеству просмотров, затем по дате создания, затем по id
            return qs.order_by("-views_count", "-created_at", "-id")
        if sort == SearchSort.POPULAR:
            # Популярность — по показам (impressions), затем по дате создания, затем по id
            return qs.order_by("-impressions_count", "-created_at", "-id")
        if sort == SearchSort.RATING_DESC:
            return qs.order_by("-average_rating", "-reviews_count", "-created_at", "-id")
        if sort == SearchSort.RATING_ASC:
            return qs.order_by("average_rating", "-created_at", "-id")
        if sort == SearchSort.REVIEWS_DESC:
            return qs.order_by("-reviews_count", "-created_at", "-id")
        if sort == SearchSort.REVIEWS_ASC:
            return qs.order_by("reviews_count", "-created_at", "-id")
        # По умолчанию — новые сверху
        return qs.order_by("-created_at", "-id")

    def search(self, q: SearchQueryDTO) -> Tuple[list[AccDomain], int]:
        qs = AccORM.objects.all()

        if q.only_active:
            qs = qs.filter(is_active=True)

        keyword = (q.keyword or "").strip()
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))

        if q.city:
            qs = qs.filter(city__icontains=q.city)
        if q.region:
            qs = qs.filter(region__icontains=q.region)

        if q.price_min is not None:
            qs = qs.filter(price_cents__gte=int(round(q.price_min * 100)))
        if q.price_max is not None:
            qs = qs.filter(price_cents__lte=int(round(q.price_max * 100)))

        if q.rooms_min is not None:
            qs = qs.filter(rooms__gte=q.rooms_min)
        if q.rooms_max is not None:
            qs = qs.filter(rooms__lte=q.rooms_max)

        if q.housing_types:
            qs = qs.filter(housing_type__in=[t.value for t in q.housing_types])

        total = qs.count()

        # Инкремент показов для всех найденных, но только если есть хоть один фильтр/keyword
        has_filters = any([
            bool(keyword),
            bool(q.city),
            bool(q.region),
            q.price_min is not None,
            q.price_max is not None,
            q.rooms_min is not None,
            q.rooms_max is not None,
            bool(q.housing_types),
        ])
        if has_filters and total > 0:
            ids = list(qs.values_list("id", flat=True))
            with transaction.atomic():
                AccORM.objects.filter(id__in=ids).update(impressions_count=F("impressions_count") + 1)

        # Сортировка — берём из q.sort
        qs = self._apply_sort(qs, q.sort)

        page = max(1, q.page)
        page_size = max(1, q.page_size)
        offset = (page - 1) * page_size
        items_qs = qs[offset: offset + page_size]

        return ([_to_domain(o) for o in items_qs], total)
