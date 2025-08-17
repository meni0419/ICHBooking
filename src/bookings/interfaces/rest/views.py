# Слой interfaces: представления/ендпоинты
from __future__ import annotations

from datetime import date

from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_protect

from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.interfaces.permissions import IsAuthenticatedAndActive

from src.shared.errors import ApplicationError
from src.shared.interfaces.api_errors import response_from_app_error

from src.users.interfaces.rest.permissions import IsGuest, IsHost

from src.bookings.interfaces.rest.serializers import BookingCreateSerializer, BookingDetailSerializer
from src.bookings.application.commands import (
    CreateBookingCommand,
    ConfirmBookingCommand,
    RejectBookingCommand,
    CancelBookingCommand,
)
from src.bookings.application.queries import ListMyBookingsQuery, ListMyRequestsForHostQuery, GetBookingByIdQuery
from src.bookings.application.use_cases.create_booking import CreateBookingUseCase
from src.bookings.application.use_cases.list_my_bookings import ListMyBookingsUseCase
from src.bookings.application.use_cases.list_my_requests import ListMyRequestsForHostUseCase
from src.bookings.application.use_cases.confirm_booking import ConfirmBookingUseCase
from src.bookings.application.use_cases.reject_booking import RejectBookingUseCase
from src.bookings.application.use_cases.cancel_booking import CancelBookingUseCase
from src.bookings.application.use_cases.get_booking import GetBookingByIdUseCase

from src.bookings.infrastructure.repositories import DjangoBookingRepository
from src.accommodations.infrastructure.repositories import DjangoAccommodationRepository


@extend_schema(
    tags=["bookings"],
    responses={200: BookingDetailSerializer, 403: OpenApiResponse(description="Forbidden"),
               404: OpenApiResponse(description="Not found")},
    operation_id="bookings_detail",
    description="Детали бронирования. Доступно только гостю или хосту, к которым относится бронь.",
)
class BookingDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, booking_id: int):
        repo = DjangoBookingRepository()
        dto = GetBookingByIdUseCase(repo).execute(GetBookingByIdQuery(booking_id=booking_id))
        # Разрешаем только участникам брони (или staff)
        if (request.user.id not in (dto.guest_id, dto.host_id)) and not getattr(request.user, "is_staff", False):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response(BookingDetailSerializer(dto).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["bookings"],
    request=BookingCreateSerializer,
    responses={201: BookingDetailSerializer, 400: OpenApiResponse(description="Bad request")},
    operation_id="bookings_create",
    description="Создать бронирование (guest). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class CreateBookingView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsGuest]

    def post(self, request):
        ser = BookingCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        accommodation_id = ser.validated_data["accommodation_id"]

        acc_repo = DjangoAccommodationRepository()
        acc = acc_repo.get_by_id(accommodation_id)
        if not acc:
            return Response({"detail": "Accommodation not found"}, status=status.HTTP_404_NOT_FOUND)

        cmd = CreateBookingCommand(
            accommodation_id=accommodation_id,
            guest_id=request.user.id,
            host_id=acc.owner_id,
            start_date=ser.validated_data["start_date"],
            end_date=ser.validated_data["end_date"],
        )
        repo = DjangoBookingRepository()
        try:
            dto = CreateBookingUseCase(repo).execute(cmd)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ApplicationError as e:
            return response_from_app_error(e)
        return Response(BookingDetailSerializer(dto).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["bookings"],
    responses={200: BookingDetailSerializer(many=True)},
    operation_id="bookings_list_me",
    description="Список моих бронирований (guest).",
)
class ListMyBookingsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsGuest]

    def get(self, request):
        repo = DjangoBookingRepository()
        dtos = ListMyBookingsUseCase(repo).execute(ListMyBookingsQuery(guest_id=request.user.id, active_only=False))
        return Response(BookingDetailSerializer(dtos, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["bookings"],
    responses={200: BookingDetailSerializer(many=True)},
    operation_id="bookings_list_requests_for_host",
    description="Список заявок со статусом requested, где я — host.",
)
class ListMyRequestsForHostView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsHost]

    def get(self, request):
        repo = DjangoBookingRepository()
        dtos = ListMyRequestsForHostUseCase(repo).execute(ListMyRequestsForHostQuery(host_id=request.user.id))
        return Response(BookingDetailSerializer(dtos, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["bookings"],
    responses={200: BookingDetailSerializer, 404: OpenApiResponse(description="Not found")},
    operation_id="bookings_confirm",
    description="Подтвердить бронирование (host). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsHost]

    def post(self, request, booking_id: int):
        repo = DjangoBookingRepository()
        cmd = ConfirmBookingCommand(booking_id=booking_id, actor_user_id=request.user.id)
        try:
            dto = ConfirmBookingUseCase(repo).execute(cmd)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ApplicationError as e:
            return response_from_app_error(e)
        return Response(BookingDetailSerializer(dto).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["bookings"],
    responses={200: BookingDetailSerializer, 404: OpenApiResponse(description="Not found")},
    operation_id="bookings_reject",
    description="Отклонить бронирование (host). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class RejectBookingView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsHost]

    def post(self, request, booking_id: int):
        repo = DjangoBookingRepository()
        cmd = RejectBookingCommand(booking_id=booking_id, actor_user_id=request.user.id)
        try:
            dto = RejectBookingUseCase(repo).execute(cmd)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ApplicationError as e:
            return response_from_app_error(e)
        return Response(BookingDetailSerializer(dto).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["bookings"],
    responses={200: BookingDetailSerializer, 404: OpenApiResponse(description="Not found")},
    operation_id="bookings_cancel",
    description="Отмена бронирования (guest или host, по правилам). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class CancelBookingView(APIView):
    permission_classes = [IsAuthenticatedAndActive]  # доступ и гостю, и хосту — домен проверит

    def post(self, request, booking_id: int):
        repo = DjangoBookingRepository()
        cmd = CancelBookingCommand(
            booking_id=booking_id,
            actor_user_id=request.user.id,
            today=date.today(),
        )
        try:
            dto = CancelBookingUseCase(repo).execute(cmd)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ApplicationError as e:
            return response_from_app_error(e)
        return Response(BookingDetailSerializer(dto).data, status=status.HTTP_200_OK)
