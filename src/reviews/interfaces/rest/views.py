from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.interfaces.permissions import IsAuthenticatedAndActive
from src.reviews.application.use_cases.get_review import GetReviewUseCase
from src.users.interfaces.rest.permissions import IsGuest

from src.reviews.interfaces.rest.serializers import (
    ReviewCreateSerializer,
    ReviewDetailSerializer,
    ReviewUpdateSerializer,
)
from src.reviews.application.commands import CreateReviewCommand, UpdateReviewCommand, DeleteReviewCommand, \
    GetReviewCommand
from src.reviews.application.queries import ListReviewsForAccommodationQuery, ListMyReviewsQuery
from src.reviews.application.use_cases.create_review import CreateReviewUseCase
from src.reviews.application.use_cases.list_reviews_for_accommodation import ListReviewsForAccommodationUseCase
from src.reviews.application.use_cases.list_my_reviews import ListMyReviewsUseCase
from src.reviews.application.use_cases.update_review import UpdateReviewUseCase
from src.reviews.application.use_cases.delete_review import DeleteReviewUseCase

from src.reviews.infrastructure.repositories import DjangoReviewRepository
from src.bookings.infrastructure.repositories import DjangoBookingRepository


@extend_schema(
    tags=["reviews"],
    request=ReviewCreateSerializer,
    responses={201: ReviewDetailSerializer, 400: OpenApiResponse(description="Bad request")},
    operation_id="reviews_create",
    description="Создать отзыв к завершённому бронированию (guest). Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class CreateReviewView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsGuest]

    def post(self, request):
        ser = ReviewCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reviews_repo = DjangoReviewRepository()
        bookings_repo = DjangoBookingRepository()
        use_case = CreateReviewUseCase(reviews=reviews_repo, bookings=bookings_repo)
        dto = use_case.execute(
            CreateReviewCommand(
                accommodation_id=ser.validated_data["accommodation_id"],
                author_id=request.user.id,
                booking_id=ser.validated_data["booking_id"],
                rating=ser.validated_data["rating"],
                text=ser.validated_data["text"],
            )
        )
        return Response(ReviewDetailSerializer(dto).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["reviews"],
    responses={200: ReviewDetailSerializer(many=True)},
    operation_id="reviews_list_for_accommodation",
    description="Список отзывов по объявлению (публично).",
)
class ListReviewsForAccommodationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, accommodation_id: int):
        reviews_repo = DjangoReviewRepository()
        use_case = ListReviewsForAccommodationUseCase(reviews=reviews_repo)
        dtos = use_case.execute(ListReviewsForAccommodationQuery(accommodation_id=accommodation_id))
        return Response(ReviewDetailSerializer(dtos, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["reviews"],
    responses={200: ReviewDetailSerializer(many=True)},
    operation_id="reviews_list_mine",
    description="Мои отзывы (guest).",
)
class ListMyReviewsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsGuest]

    def get(self, request):
        reviews_repo = DjangoReviewRepository()
        use_case = ListMyReviewsUseCase(reviews=reviews_repo)
        dtos = use_case.execute(ListMyReviewsQuery(author_id=request.user.id))
        return Response(ReviewDetailSerializer(dtos, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["reviews"],
    request=ReviewUpdateSerializer,
    responses={200: ReviewDetailSerializer, 404: OpenApiResponse(description="Not found")},
    operation_id="reviews_update",
    description="Обновить свой отзыв (guest). Требуется CSRF.",
)
@extend_schema(
    tags=["reviews"],
    responses={204: OpenApiResponse(description="Deleted"), 404: OpenApiResponse(description="Not found")},
    operation_id="reviews_delete",
    description="Удалить свой отзыв (guest). Требуется CSRF.",
)
@extend_schema(
    tags=["reviews"],
    responses={200: ReviewDetailSerializer, 404: OpenApiResponse(description="Not found")},
    operation_id="reviews_get",
    description="Получить свой отзыв (guest).",
    methods=["GET"],
)
class GetUpdateDeleteReviewView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsGuest]

    def get(self, request, review_id: int):
        reviews_repo = DjangoReviewRepository()
        use_case = GetReviewUseCase(reviews=reviews_repo)
        dto = use_case.execute(GetReviewCommand(review_id=review_id, actor_user_id=request.user.id))
        return Response(ReviewDetailSerializer(dto).data, status=status.HTTP_200_OK)

    @method_decorator(csrf_protect)
    def patch(self, request, review_id: int):
        ser = ReviewUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        reviews_repo = DjangoReviewRepository()
        use_case = UpdateReviewUseCase(reviews=reviews_repo)
        dto = use_case.execute(
            UpdateReviewCommand(
                review_id=review_id,
                actor_user_id=request.user.id,
                rating=ser.validated_data.get("rating"),
                text=ser.validated_data.get("text"),
            )
        )
        return Response(ReviewDetailSerializer(dto).data, status=status.HTTP_200_OK)

    @method_decorator(csrf_protect)
    def delete(self, request, review_id: int):
        reviews_repo = DjangoReviewRepository()
        use_case = DeleteReviewUseCase(reviews=reviews_repo)
        use_case.execute(DeleteReviewCommand(review_id=review_id, actor_user_id=request.user.id))
        return Response(status=status.HTTP_204_NO_CONTENT)
