import os

# ...existing code...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME', 'dusangire_db'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', '1234567890'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),  # Changed from 'db' to 'localhost'
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}