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

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Стартуем gunicorn — статику отдаёт WhiteNoise
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout ${GUNICORN_TIMEOUT:-120}