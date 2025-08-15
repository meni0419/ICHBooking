from __future__ import annotations

from datetime import date

from src.shared.errors import ApplicationError
from src.reviews.application.commands import CreateReviewCommand
from src.reviews.application.mappers import to_dto
from src.reviews.domain.dtos import ReviewDTO
from src.reviews.domain.repository_interfaces import IReviewRepository
from src.reviews.domain.services import create_review as domain_create_review
from src.reviews.domain.value_objects import Rating
from src.bookings.domain.repository_interfaces import IBookingRepository
from src.bookings.domain.entities import BookingStatus


class CreateReviewUseCase:
    def __init__(
            self,
            reviews: IReviewRepository,
            bookings: IBookingRepository,
    ):
        self._reviews = reviews
        self._bookings = bookings

    def execute(self, cmd: CreateReviewCommand) -> ReviewDTO:
        try:
            booking = self._bookings.get_by_id(cmd.booking_id)
            if not booking:
                raise ApplicationError("Booking not found")

            belongs = (
                    booking.guest_id == cmd.author_id and booking.accommodation_id == cmd.accommodation_id
            )

            today = date.today()
            is_completed = booking.status == BookingStatus.COMPLETED

            is_unique_for_booking = not self._reviews.exists_for_booking(cmd.booking_id)

            entity = domain_create_review(
                accommodation_id=cmd.accommodation_id,
                author_id=cmd.author_id,
                booking_id=cmd.booking_id,
                rating=Rating(cmd.rating),
                text=cmd.text,
                booking_belongs_to_author_and_accommodation=belongs,
                booking_is_completed=is_completed,
                is_unique_for_booking=is_unique_for_booking,
            )

            created = self._reviews.create(entity)
            return to_dto(created)
        except ApplicationError:
            raise
        except Exception as ex:
            raise ApplicationError(str(ex))
