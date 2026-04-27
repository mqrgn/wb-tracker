#!/bin/bash

# Останавливаем скрипт при ошибке
set -e

echo "Waiting for PostgreSQL to start..."
# Мы используем netcat (nc), который установили в Dockerfile
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL started!"

echo "Applying database migrations..."
alembic -c app/alembic.ini upgrade head

# НАПОЛНЕНИЕ БАЗЫ:
echo "Seeding initial data..."
export PYTHONPATH=$PYTHONPATH:/app
python app/seed_db.py

echo "Starting FastApi and Bot..."

# Запускаем основной файл (убедись, что в main.py прописан запуск uvicorn или бота)
export PYTHONPATH=$PYTHONPATH:/app
python app/main.py