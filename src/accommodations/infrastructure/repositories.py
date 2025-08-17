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
        comments_count=getattr(obj, "review_count", 0),
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
            qs = AccORM.objects.filter(pk=acc_id).annotate(review_count=Count("reviews"))
            return _to_domain(qs.get())
        except AccORM.DoesNotExist:
            return None

    def list_by_owner(self, owner_id: int, active_only: bool = False) -> list[AccDomain]:
        qs = AccORM.objects.filter(owner_id=owner_id)
        if active_only:
            qs = qs.filter(is_active=True)
        qs = qs.annotate(review_count=Count("reviews")).order_by("-created_at")
        return [_to_domain(o) for o in qs]

    def search_ids(self, ids: Iterable[int]) -> list[AccDomain]:
        qs = AccORM.objects.filter(id__in=list(ids)).annotate(review_count=Count("reviews"))
        return [_to_domain(o) for o in qs]

    def create(self, acc: AccDomain) -> AccDomain:
        obj = AccORM(owner_id=acc.owner_id)
        obj = _apply_domain(acc, obj)
        obj.save()
        return _to_domain(AccORM.objects.annotate(review_count=Count("reviews")).get(pk=obj.id))

    def update(self, acc: AccDomain) -> AccDomain:
        obj = AccORM.objects.get(pk=acc.id)
        obj = _apply_domain(acc, obj)
        obj.save()
        return _to_domain(AccORM.objects.annotate(review_count=Count("reviews")).get(pk=obj.id))

    def delete(self, acc_id: int, owner_id: Optional[int] = None) -> None:
        qs = AccORM.objects.filter(pk=acc_id)
        if owner_id is not None:
            qs = qs.filter(owner_id=owner_id)
        qs.delete()

    def increment_views(self, acc_id: int) -> None:
        AccORM.objects.filter(pk=acc_id).update(views_count=F("views_count") + 1)

    def search(self, q: SearchQueryDTO) -> Tuple[list[AccDomain], int]:
        qs: QuerySet[AccORM] = AccORM.objects.all()

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

        # Для выдачи добавляем количество отзывов
        qs = qs.annotate(review_count=Count("reviews"))

        # Сортировки
        if q.sort == SearchSort.PRICE_ASC:
            qs = qs.order_by("price_cents", "-id")
        elif q.sort == SearchSort.PRICE_DESC:
            qs = qs.order_by("-price_cents", "-id")
        elif q.sort == SearchSort.CREATED_AT_ASC:
            qs = qs.order_by("created_at", "id")
        elif q.sort == SearchSort.POPULAR:
            qs = qs.order_by("-impressions_count", "-created_at", "-id")
        elif q.sort == SearchSort.VIEWS:
            qs = qs.order_by("-views_count", "-created_at", "-id")
        elif q.sort == SearchSort.COMMENTS:
            qs = qs.order_by("-review_count", "-created_at", "-id")
        else:
            qs = qs.order_by("-created_at", "-id")

        page = max(1, q.page)
        page_size = max(1, q.page_size)
        offset = (page - 1) * page_size
        items_qs = qs[offset: offset + page_size]

        return ([_to_domain(o) for o in items_qs], total)
