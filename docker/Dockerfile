# docker/Dockerfile
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

# Копируем проект (если понадобятся локальные колёса/сборка)
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

RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /app && chown app:app /app
WORKDIR /app

# Копируем готовое venv из builder (быстро, без повторной установки)
COPY --from=builder /opt/venv /opt/venv

# Затем основной код сразу с нужным владельцем
COPY --chown=app:app . /app

USER app

EXPOSE 8000

# если entrypoint исполняемый (+x в репо)
#CMD ["docker/entrypoint.sh"]
# если не менять права в гите:
CMD ["sh", "docker/entrypoint.sh"]