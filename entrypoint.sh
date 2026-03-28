#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate --no-input

echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn school_backend.wsgi \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-file -
