#!/bin/sh
echo "Ожидание..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL запущен"

python ingest_data.py
flask run --host=0.0.0.0
   
