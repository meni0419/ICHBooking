#!/usr/bin/env sh
set -e

# Ожидание MySQL
if [ -n "${DB_HOST}" ]; then
  DB_WAIT_HOST="${DB_HOST}"
  if [ "${DB_WAIT_HOST}" = "db" ]; then
    DB_WAIT_PORT="3306"
  else
    DB_WAIT_PORT="${DB_PORT:-3306}"
  fi
  echo "Waiting for ${DB_WAIT_HOST}:${DB_WAIT_PORT}..."
  i=1
  while [ "$i" -le 60 ]; do
    if nc -z "${DB_WAIT_HOST}" "${DB_WAIT_PORT}"; then
      echo "DB is up"
      break
    fi
    i=$((i + 1))
    sleep 1
  done
fi

# Управляем запуском миграций/статик через переменные окружения
# RUN_MIGRATIONS=true|false, RUN_COLLECTSTATIC=true|false
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  python manage.py migrate --noinput
else
  echo "Skipping migrations (RUN_MIGRATIONS=false)"
fi

if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
  # Собираем статику только если она ещё не собрана (ускоряет рестарты)
  if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles 2>/dev/null || true)" ]; then
    python manage.py collectstatic --noinput
  else
    echo "Staticfiles already present, skipping collectstatic"
  fi
else
  echo "Skipping collectstatic (RUN_COLLECTSTATIC=false)"
fi

# Стартуем gunicorn — статику отдаёт WhiteNoise
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout ${GUNICORN_TIMEOUT:-120}
