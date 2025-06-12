#!/bin/bash

# Wait for database
until nc -z db 5432; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo "PostgreSQL started"

# Apply database migrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@gmail.com',
        password='admin123'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Start application
exec "$@"
