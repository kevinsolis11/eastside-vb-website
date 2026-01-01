#!/bin/bash
# Railway deployment startup script

set -e

echo "Collecting static files..."
python volleyball_site/manage.py collectstatic --noinput

echo "Running migrations..."
python volleyball_site/manage.py migrate --noinput

echo "Creating superuser if not exists..."
python volleyball_site/manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created: admin / admin123')
else:
    print('Admin user already exists')
END

echo "Deployment preparation complete!"
