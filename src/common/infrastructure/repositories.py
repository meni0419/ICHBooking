# Слой infrastructure: реализации репозиториев (Django ORM), адаптеры для domain.repository_interfaces
# src/common/infrastructure/repositories.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from django.db.models import Count, QuerySet, Max  # добавили Max

from src.common.infrastructure.orm.models import SearchQueryLog


def _norm_str(x: Optional[str]) -> str:
    return (x or "").strip()


def _norm_list_str(xs: Optional[List[str]]) -> List[str]:
    xs = xs or []
    xs = [(_norm_str(x)) for x in xs if _norm_str(x)]
    return sorted(list(dict.fromkeys(xs)))  # uniq + sort


def build_query_signature(
        *,
        keyword: Optional[str],
        city: Optional[str],
        region: Optional[str],
        price_min: Optional[float],
        price_max: Optional[float],
        rooms_min: Optional[int],
        rooms_max: Optional[int],
        housing_types: Optional[List[str]],
) -> Dict[str, Any]:
    norm = {
        "keyword": _norm_str(keyword),
        "city": _norm_str(city),
        "region": _norm_str(region),
        "price_min": price_min if price_min is not None else None,
        "price_max": price_max if price_max is not None else None,
        "rooms_min": rooms_min if rooms_min is not None else None,
        "rooms_max": rooms_max if rooms_max is not None else None,
        "housing_types": _norm_list_str(housing_types),
    }
    parts: List[str] = []
    for k in ("keyword", "city", "region", "price_min", "price_max", "rooms_min", "rooms_max"):
        v = norm[k]
        if v not in (None, ""):
            parts.append(f"{k}={v}")
    if norm["housing_types"]:
        parts.append(f"housing_types={','.join(norm['housing_types'])}")
    signature = "|".join(parts)
    return {"norm": norm, "signature": signature}


def log_search_query(
        *,
        user_id: Optional[int],
        keyword: Optional[str],
        city: Optional[str],
        region: Optional[str],
        price_min: Optional[float],
        price_max: Optional[float],
        rooms_min: Optional[int],
        rooms_max: Optional[int],
        housing_types: Optional[List[str]],
) -> None:
    built = build_query_signature(
        keyword=keyword,
        city=city,
        region=region,
        price_min=price_min,
        price_max=price_max,
        rooms_min=rooms_min,
        rooms_max=rooms_max,
        housing_types=housing_types,
    )
    norm = built["norm"]
    signature = built["signature"]
    if not signature:
        return
    SearchQueryLog.objects.create(
        user_id=user_id,
        keyword=norm["keyword"],
        city=norm["city"],
        region=norm["region"],
        price_min=norm["price_min"],
        price_max=norm["price_max"],
        rooms_min=norm["rooms_min"],
        rooms_max=norm["rooms_max"],
        housing_types_csv=",".join(norm["housing_types"]) if norm["housing_types"] else "",
        query_signature=signature,
    )


def list_popular_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """
    ТОП популярных нормализованных запросов, сгруппированных по query_signature.
    Берём представительные параметры через агрегаты (Max).
    """
    qs: QuerySet = (
        SearchQueryLog.objects.values("query_signature")
        .annotate(
            count=Count("*"),
            keyword=Max("keyword"),
            city=Max("city"),
            region=Max("region"),
            price_min=Max("price_min"),
            price_max=Max("price_max"),
            rooms_min=Max("rooms_min"),
            rooms_max=Max("rooms_max"),
            housing_types_csv=Max("housing_types_csv"),
        )
        .order_by("-count", "-query_signature")
    )[:limit]

    results: List[Dict[str, Any]] = []
    for row in qs:
        params: Dict[str, Any] = {}
        if row["keyword"]:
            params["keyword"] = row["keyword"]
        if row["city"]:
            params["city"] = row["city"]
        if row["region"]:
            params["region"] = row["region"]
        if row["price_min"] is not None:
            params["price_min"] = row["price_min"]
        if row["price_max"] is not None:
            params["price_max"] = row["price_max"]
        if row["rooms_min"] is not None:
            params["rooms_min"] = row["rooms_min"]
        if row["rooms_max"] is not None:
            params["rooms_max"] = row["rooms_max"]
        if row["housing_types_csv"]:
            for ht in row["housing_types_csv"].split(","):
                if ht:
                    params.setdefault("housing_types", []).append(ht)

        # Сериализуем в querystring с повторяющимися ключами
        flat_params: List[tuple] = []
        for k, v in params.items():
            if isinstance(v, list):
                for item in v:
                    flat_params.append((k, item))
            else:
                flat_params.append((k, v))
        querystring = urlencode(flat_params)

        results.append(
            {"count": row["count"], "params": params, "querystring": querystring}
        )
    return results
