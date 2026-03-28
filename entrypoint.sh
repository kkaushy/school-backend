#!/bin/sh
set -e

echo "PORT=${PORT:-8000}"
echo "DB_HOST=${DB_HOST}"
echo "Starting gunicorn..."

exec gunicorn school_backend.wsgi \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-file -
