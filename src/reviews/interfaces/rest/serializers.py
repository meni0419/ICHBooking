# Слой interfaces: DRF сериалайзеры (если используете DRF)
from __future__ import annotations

from rest_framework import serializers


class ReviewCreateSerializer(serializers.Serializer):
    accommodation_id = serializers.IntegerField(required=False)
    booking_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField(min_length=3, max_length=5000)


class ReviewDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    accommodation_id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    booking_id = serializers.IntegerField()
    rating = serializers.IntegerField()
    text = serializers.CharField()
    created_at = serializers.DateTimeField()


class ReviewUpdateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    text = serializers.CharField(min_length=3, max_length=5000, required=False)
