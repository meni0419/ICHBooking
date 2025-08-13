# Реэкспорт ORM-модели, чтобы Django "видел" её как src.accommodations.models.Accommodation
from .infrastructure.orm.models import Accommodation

__all__ = ["Accommodation"]