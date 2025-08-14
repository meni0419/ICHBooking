from __future__ import annotations

from src.accommodations.application.dtos import SearchResultDTO, SearchPageDTO
from src.accommodations.application.mappers import to_dto
from src.accommodations.application.queries import SearchAccommodationsQuery
from src.accommodations.domain.dtos import SearchQueryDTO
from src.accommodations.domain.repository_interfaces import IAccommodationRepository
from src.accommodations.domain.services import normalize_search_query


class SearchAccommodationsUseCase:
    def __init__(self, repo: IAccommodationRepository):
        self._repo = repo

    def execute(self, q: SearchAccommodationsQuery) -> SearchResultDTO:
        # Приводим к доменному DTO и нормализуем
        domain_q = SearchQueryDTO(
            keyword=q.keyword,
            price_min=q.price_min,
            price_max=q.price_max,
            city=q.city,
            region=q.region,
            rooms_min=q.rooms_min,
            rooms_max=q.rooms_max,
            housing_types=list(q.housing_types or []),
            only_active=q.only_active,
            sort=q.sort,
            page=q.page,
            page_size=q.page_size,
        )
        domain_q = normalize_search_query(domain_q)

        # Выполняем поиск через репозиторий
        items, total = self._repo.search(domain_q)

        # Маппинг + страница
        dto_items = [to_dto(a) for a in items]
        page = SearchPageDTO(page=domain_q.page, page_size=domain_q.page_size, total=total)
        return SearchResultDTO(items=dto_items, page=page)