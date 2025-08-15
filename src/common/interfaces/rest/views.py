# Слой interfaces: представления/ендпоинты
from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.interfaces.rest.serializers import PopularSearchItemSerializer
from src.common.infrastructure.repositories import list_popular_queries


@extend_schema(
    tags=["search"],
    responses={200: PopularSearchItemSerializer(many=True)},
    operation_id="search_popular",
    description="ТОП популярных поисковых запросов (нормализовано).",
)
class PopularSearchesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        limit = int(request.query_params.get("limit", "20"))
        data = list_popular_queries(limit=limit)
        return Response(PopularSearchItemSerializer(data, many=True).data, status=status.HTTP_200_OK)


@extend_schema(tags=["utils"], operation_id="set_csrf_cookie", description="Устанавливает csrftoken cookie",
               responses={204: None})
@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfCookieView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(status=204)
