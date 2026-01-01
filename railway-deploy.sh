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
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Admin user created: admin / admin123')
    else:
        # Update password just in case
        user = User.objects.get(username='admin')
        user.set_password('admin123')
        user.save()
        print('✅ Admin user already exists, password verified')
except Exception as e:
    print(f'Error creating admin: {e}')
END

echo "Deployment preparation complete!"
