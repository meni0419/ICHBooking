# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Системные зависимости: mysqlclient требует компилятор, dev-библиотеки и pkg-config.
# Также ставим netcat для ожидания БД.
RUN apt-get update && apt-get install -y \
    build-essential default-libmysqlclient-dev pkg-config \
    curl netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и ставим их
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

FROM
# Копируем весь проект (контекст сборки — корень репозитория)
COPY .. /app

# Гарантируем, что entrypoint исполняемый
RUN chmod +x docker/entrypoint.sh

EXPOSE 8000
CMD ["docker/entrypoint.sh"]