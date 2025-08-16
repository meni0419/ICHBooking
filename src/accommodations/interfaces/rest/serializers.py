# Слой interfaces: DRF сериалайзеры
from __future__ import annotations

from rest_framework import serializers

from src.accommodations.domain.value_objects import HousingType
from src.accommodations.domain.dtos import SearchSort


class AccommodationCreateUpdateSerializer(serializers.Serializer):
    # owner_id берём из request.user на уровне вьюхи
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    city = serializers.CharField(max_length=120)
    region = serializers.CharField(max_length=120)
    price_eur = serializers.FloatField(min_value=0.01)
    rooms = serializers.IntegerField(min_value=1, max_value=100)
    housing_type = serializers.ChoiceField(
        choices=[(e.value, e.value) for e in HousingType]
    )
    is_active = serializers.BooleanField(required=False)


class AccommodationPartialUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    city = serializers.CharField(max_length=120, required=False)
    region = serializers.CharField(max_length=120, required=False)
    price_eur = serializers.FloatField(min_value=0.01, required=False)
    rooms = serializers.IntegerField(min_value=1, max_value=100, required=False)
    housing_type = serializers.ChoiceField(
        choices=[(e.value, e.value) for e in HousingType], required=False
    )
    is_active = serializers.BooleanField(required=False)


class AccommodationDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    owner_id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    city = serializers.CharField()
    region = serializers.CharField()
    country = serializers.CharField()
    price_eur = serializers.FloatField()
    rooms = serializers.IntegerField()
    housing_type = serializers.CharField()
    is_active = serializers.BooleanField()
    impressions_count = serializers.IntegerField()
    views_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()


class SearchQueryParamsSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False, allow_blank=True)
    price_min = serializers.FloatField(required=False, min_value=0.0)
    price_max = serializers.FloatField(required=False, min_value=0.0)
    city = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    rooms_min = serializers.IntegerField(required=False, min_value=0)
    rooms_max = serializers.IntegerField(required=False, min_value=0)
    housing_types = serializers.ListField(
        child=serializers.ChoiceField(choices=[(e.value, e.value) for e in HousingType]),
        required=False
    )
    only_active = serializers.BooleanField(required=False, default=True)
    sort = serializers.ChoiceField(
        choices=[(s.value, s.value) for s in SearchSort],
        required=False,
        default=SearchSort.CREATED_AT_DESC.value,
    )
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)


class SearchPageSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total = serializers.IntegerField()


class SearchResultSerializer(serializers.Serializer):
    items = AccommodationDetailSerializer(many=True)
    page = SearchPageSerializer()
