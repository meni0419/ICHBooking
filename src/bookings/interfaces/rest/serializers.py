# Слой interfaces: DRF сериалайзеры (если используете DRF)
from __future__ import annotations

from rest_framework import serializers

from src.bookings.domain.entities import BookingStatus


class BookingCreateSerializer(serializers.Serializer):
    accommodation_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class BookingDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    accommodation_id = serializers.IntegerField()
    guest_id = serializers.IntegerField()
    host_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    status = serializers.ChoiceField(choices=[(s.value, s.value) for s in BookingStatus])
