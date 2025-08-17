from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response

from src.shared.errors import ApplicationError


def response_from_app_error(e: ApplicationError) -> Response:
    """
    Конвертирует ApplicationError в корректный HTTP-ответ.
    Простейшее эвристическое сопоставление по сообщению.
    """
    msg = str(e)
    ml = msg.lower()
    if "not found" in ml:
        return Response({"detail": msg}, status=status.HTTP_404_NOT_FOUND)
    if "forbidden" in ml or "permission" in ml or "only host" in ml or "only guest" in ml or "not the author" in ml:
        return Response({"detail": msg}, status=status.HTTP_403_FORBIDDEN)
    return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)


def response_from_value_error(e: ValueError) -> Response:
    msg = str(e)
    ml = msg.lower()
    if "not found" in ml:
        return Response({"detail": msg}, status=status.HTTP_404_NOT_FOUND)
    if "not the author" in ml:
        return Response({"detail": msg}, status=status.HTTP_403_FORBIDDEN)
    return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
