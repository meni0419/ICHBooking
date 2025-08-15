# Слой infrastructure: Django модели ORM, связанные с domain через маппинг (не переносить доменные сущности)
from __future__ import annotations

from django.conf import settings
from django.db import models


class SearchQueryLog(models.Model):
    """
    Лог поискового запроса (только при наличии фильтров/keyword).
    Нормализуем и строим query_signature (агрегация по одинаковым запросам).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="search_logs", db_index=True
    )

    # Параметры запроса (нормализованные)
    keyword = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=120, blank=True, default="")
    region = models.CharField(max_length=120, blank=True, default="")
    price_min = models.FloatField(null=True, blank=True)
    price_max = models.FloatField(null=True, blank=True)
    rooms_min = models.IntegerField(null=True, blank=True)
    rooms_max = models.IntegerField(null=True, blank=True)
    housing_types_csv = models.CharField(max_length=255, blank=True, default="")  # "apartment,studio"

    # Нормализованный ключ (сигнатура) для агрегации
    query_signature = models.CharField(max_length=255, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "search_query_logs"
        indexes = [
            models.Index(fields=["query_signature", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"SearchLog[{self.query_signature}]"
