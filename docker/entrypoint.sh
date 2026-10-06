#!/bin/bash
set -e

echo "Waiting for Postgres..."
while ! pg_isready -h postgres -U wizard -d wizard_db; do
  sleep 1
done

echo "Waiting for Redis..."
while ! redis-cli -h redis ping > /dev/null 2>&1; do
  sleep 1
done

echo "Running migrations..."
python -m alembic upgrade head || true

echo "Services ready, starting application..."
exec "$@"
