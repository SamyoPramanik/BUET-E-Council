#!/bin/sh

# Stop the script if any command fails
set -e

echo "⏳ Waiting for database to be ready..."

# We use 'nc' (netcat) to check if the DB port is open
# Replace 'db' with your database service name from podman-compose
# Replace '5432' with your DB port (5432 for Postgres, 3306 for MariaDB)
while ! nc -z db 5432; do
  sleep 0.5
done

echo "✅ Database is up!"

# 1. Run the modular seeding script
# This now runs safely because we know the DB is listening
echo "🌱 Seeding the database..."
PYTHONPATH=. uv run python scripts/run_seed.py

# 2. Start the FastAPI application with Hot Reload
echo "🚀 Starting FastAPI server..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000