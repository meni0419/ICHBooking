# Слой interfaces: DRF сериалайзеры
from __future__ import annotations

from rest_framework import serializers

from src.accommodations.domain.value_objects import HousingType


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