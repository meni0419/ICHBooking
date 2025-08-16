from __future__ import annotations

from typing import Dict
from rest_framework.test import APIClient


def ensure_csrf(client: APIClient) -> Dict[str, str]:
    """
    Получает csrftoken через /api/csrf/ и возвращает заголовки для небезопасных методов.
    Использование:
        headers = ensure_csrf(client)
        client.post(url, data, format='json', **headers)
    """
    # Установит csrftoken в cookie
    resp = client.get("/api/csrf/")
    assert resp.status_code in (200, 204), f"Cannot obtain CSRF: {resp.status_code}"
    csrftoken = None
    # Django TestClient хранит куки в client.cookies
    if "csrftoken" in client.cookies:
        csrftoken = client.cookies["csrftoken"].value
    else:
        # На всякий: иногда set-cookie пишет имя заглавными
        for k in client.cookies.keys():
            if k.lower() == "csrftoken":
                csrftoken = client.cookies[k].value
                break
    assert csrftoken, "CSRF cookie not set"
    return {"HTTP_X_CSRFTOKEN": csrftoken}