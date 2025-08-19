# syntax=docker/dockerfile:1

############################
# Stage 1: builder (alpine)
############################
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv

# Build deps для mysqlclient и прочих колёс
RUN apk add --no-cache \
    build-base \
    mariadb-connector-c-dev \
    linux-headers

# Виртуальное окружение
RUN python -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:$PATH"

WORKDIR /app

# Копируем зависимости и ставим их
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект (для сборки wheel-ов локальных пакетов, если появятся; не увеличит финальный размер)
COPY . /app


############################
# Stage 2: runtime (alpine)
############################
FROM python:3.13-alpine AS runtime

# Только runtime-зависимости (mysqlclient runtime, netcat для wait)
RUN apk add --no-cache \
    mariadb-connector-c \
    netcat-openbsd

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Несистемный пользователь
RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

# Переносим готовое venv из builder
COPY --from=builder /opt/venv /opt/venv

# Код проекта
COPY . /app

# Права
RUN chown -R app:app /app && chmod +x docker/entrypoint.sh
USER app

EXPOSE 8000

# Запуск через entrypoint: миграции, collectstatic, потом gunicorn
CMD ["docker/entrypoint.sh"]