from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Review
from src.accommodations.infrastructure.orm.models import Accommodation


def _quantize_rating(value: float | None) -> Decimal:
    if not value:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def update_accommodation_rating(accommodation_id: int) -> None:
    agg = Review.objects.filter(accommodation_id=accommodation_id).aggregate(
        avg=Avg("rating"),
        cnt=Count("id"),
    )
    avg = _quantize_rating(agg["avg"])
    cnt = int(agg["cnt"] or 0)

    # Обновляем денормализованные поля атомарно
    Accommodation.objects.filter(id=accommodation_id).update(
        average_rating=avg,
        reviews_count=cnt,
    )


@receiver(post_save, sender=Review)
def on_review_saved(sender, instance: Review, **kwargs):
    # Используем on_commit, чтобы гарантировать наличие записанного отзыва
    transaction.on_commit(lambda: update_accommodation_rating(instance.accommodation_id))


@receiver(post_delete, sender=Review)
def on_review_deleted(sender, instance: Review, **kwargs):
    transaction.on_commit(lambda: update_accommodation_rating(instance.accommodation_id))