#!/bin/sh
set -e

echo "Waiting for MySQL at ${DB_HOST:-db}:${DB_PORT:-3306}..."

python <<'PY'
import os
import time

import MySQLdb

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))
user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

for attempt in range(60):
    try:
        conn = MySQLdb.connect(
            host=host,
            port=port,
            user=user,
            passwd=password,
            db=db_name,
            connect_timeout=3,
        )
        conn.close()
        print("MySQL is ready.")
        break
    except MySQLdb.OperationalError as exc:
        print(f"MySQL not ready yet ({attempt + 1}/60): {exc}")
        time.sleep(2)
else:
    raise SystemExit("MySQL did not become ready in time.")
PY

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting application..."
exec "$@"
