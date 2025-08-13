# Слой interfaces: представления/ендпоинты
# Python
# src/accommodations/interfaces/rest/views.py
from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accommodations.interfaces.rest.serializers import (
    AccommodationCreateUpdateSerializer,
    AccommodationPartialUpdateSerializer,
    AccommodationDetailSerializer,
)
from src.accommodations.interfaces.rest.permissions import IsAuthenticatedAndActive, IsHost
from src.accommodations.application.commands import (
    CreateAccommodationCommand, UpdateAccommodationCommand, DeleteAccommodationCommand, ToggleAvailabilityCommand
)
from src.accommodations.application.queries import GetAccommodationByIdQuery
from src.accommodations.application.use_cases.create_accommodation import CreateAccommodationUseCase
from src.accommodations.application.use_cases.update_accommodation import UpdateAccommodationUseCase
from src.accommodations.application.use_cases.delete_accommodation import DeleteAccommodationUseCase
from src.accommodations.application.use_cases.toggle_availability import ToggleAvailabilityUseCase
from src.accommodations.application.use_cases.get_accommodation import GetAccommodationByIdUseCase
from src.accommodations.application.mappers import to_dto
from src.accommodations.infrastructure.repositories import DjangoAccommodationRepository


@extend_schema(
    tags=["accommodations"],
    request=AccommodationCreateUpdateSerializer,
    responses={201: AccommodationDetailSerializer},
    operation_id="accommodations_create",
    description="Создать объявление (host). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class CreateAccommodationView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsHost]

    def post(self, request):
        ser = AccommodationCreateUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        repo = DjangoAccommodationRepository()
        dto = CreateAccommodationUseCase(repo).execute(
            CreateAccommodationCommand(
                owner_id=request.user.id,
                title=ser.validated_data["title"],
                description=ser.validated_data["description"],
                city=ser.validated_data["city"],
                region=ser.validated_data["region"],
                price_eur=ser.validated_data["price_eur"],
                rooms=ser.validated_data["rooms"],
                housing_type=ser.validated_data["housing_type"],
                is_active=ser.validated_data.get("is_active", True),
            )
        )
        return Response(AccommodationDetailSerializer(dto).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["accommodations"],
    responses={200: AccommodationDetailSerializer, 404: OpenApiResponse(description="Not found")},
    operation_id="accommodations_get_by_id",
)
@extend_schema(
    tags=["accommodations"],
    request=AccommodationPartialUpdateSerializer,
    responses={200: AccommodationDetailSerializer, 404: OpenApiResponse(description="Not found")},
    operation_id="accommodations_update",
    methods=["PATCH"],
    description="Обновить объявление (только владелец). Требуется CSRF.",
)
@extend_schema(
    tags=["accommodations"],
    responses={204: OpenApiResponse(description="Deleted")},
    operation_id="accommodations_delete",
    methods=["DELETE"],
    description="Удалить объявление (только владелец). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class AccommodationDetailView(APIView):
    # GET доступен всем; PATCH/DELETE — только host. Проверим по методу:
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticatedAndActive(), IsHost()]
        return [permissions.AllowAny()]

    def get(self, request, acc_id: int):
        repo = DjangoAccommodationRepository()
        dto = GetAccommodationByIdUseCase(repo).execute(GetAccommodationByIdQuery(id=acc_id))
        return Response(AccommodationDetailSerializer(dto).data, status=status.HTTP_200_OK)

    def patch(self, request, acc_id: int):
        ser = AccommodationPartialUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        repo = DjangoAccommodationRepository()
        dto = UpdateAccommodationUseCase(repo).execute(
            UpdateAccommodationCommand(
                id=acc_id,
                owner_id=request.user.id,
                title=ser.validated_data.get("title"),
                description=ser.validated_data.get("description"),
                city=ser.validated_data.get("city"),
                region=ser.validated_data.get("region"),
                price_eur=ser.validated_data.get("price_eur"),
                rooms=ser.validated_data.get("rooms"),
                housing_type=ser.validated_data.get("housing_type"),
                is_active=ser.validated_data.get("is_active"),
            )
        )
        return Response(AccommodationDetailSerializer(dto).data, status=status.HTTP_200_OK)

    def delete(self, request, acc_id: int):
        repo = DjangoAccommodationRepository()
        DeleteAccommodationUseCase(repo).execute(DeleteAccommodationCommand(id=acc_id, owner_id=request.user.id))
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["accommodations"],
    request=None,
    responses={200: AccommodationDetailSerializer},
    operation_id="accommodations_toggle_availability",
    description="Переключить/установить видимость (только владелец). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class ToggleAvailabilityView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsHost]

    def post(self, request, acc_id: int):
        value = request.data.get("is_active", None)
        if isinstance(value, str):
            value = value.lower() in ("1", "true", "yes", "on")
        elif value is not None:
            value = bool(value)
        repo = DjangoAccommodationRepository()
        dto = ToggleAvailabilityUseCase(repo).execute(
            ToggleAvailabilityCommand(id=acc_id, owner_id=request.user.id, value=value)
        )
        return Response(AccommodationDetailSerializer(dto).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["accommodations"],
    responses={200: AccommodationDetailSerializer(many=True)},
    operation_id="accommodations_list_mine",
    description="Список объявлений текущего владельца (host).",
)
class ListMyAccommodationsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsHost]

    def get(self, request):
        repo = DjangoAccommodationRepository()
        accs = repo.list_by_owner(owner_id=request.user.id, active_only=False)
        data = [AccommodationDetailSerializer(to_dto(a)).data for a in accs]
        return Response(data, status=status.HTTP_200_OK)
