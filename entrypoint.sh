#!/bin/sh

echo "=== Connectivity Test ==="
python3 -c "
import socket, os
hosts = [
    os.environ.get('DB_HOST', 'not-set'),
    'dpg-d73plplm5p6s73es5jvg-a',
    'dpg-d73plplm5p6s73es5jvg-a.singapore-postgres.render.com',
]
for h in hosts:
    try:
        info = socket.getaddrinfo(h, 5432, socket.AF_UNSPEC, socket.SOCK_STREAM)
        print(f'RESOLVED {h} -> {[x[4][0] for x in info]}')
    except Exception as e:
        print(f'FAILED   {h} -> {e}')
"

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
