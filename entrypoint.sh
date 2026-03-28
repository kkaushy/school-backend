#!/bin/sh

echo "=== School Backend Starting ==="
echo "PORT=${PORT:-8000}, DB_HOST=${DB_HOST}, DB_PORT=${DB_PORT}"

echo "Running database migrations..."
python manage.py migrate --no-input
MIGRATE_EXIT=$?

if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "WARNING: Migrations failed (exit $MIGRATE_EXIT). Starting gunicorn anyway."
else
    echo "Migrations complete."
fi

echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn school_backend.wsgi \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-file -
