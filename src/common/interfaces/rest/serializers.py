# Слой interfaces: DRF сериалайзеры (если используете DRF)
from __future__ import annotations

from rest_framework import serializers


class PopularSearchItemSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    params = serializers.JSONField()
    querystring = serializers.CharField()
