#!/bin/sh
set -e

echo "Waiting for database..."
python manage.py wait_for_db 2>/dev/null || true

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
fi

echo "Starting server..."
exec "$@"
