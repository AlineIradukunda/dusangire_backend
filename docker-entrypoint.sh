#!/bin/bash

# Wait for database
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for database..."
  sleep 1
done

echo "Database started"

python manage.py migrate
python manage.py createsuperuser --noinput || true

exec "$@"
