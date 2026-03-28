#!/bin/sh

echo "=== Running Migrations ==="
python manage.py migrate --no-input
MIGRATE_EXIT=$?
if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "WARNING: Migrations failed (exit $MIGRATE_EXIT)"
else
    echo "Migrations complete."
fi

echo "=== Starting gunicorn on port ${PORT:-8000} ==="
exec gunicorn school_backend.wsgi \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-file -
