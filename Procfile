web: cd volleyball_site && gunicorn volleyball_site.wsgi --bind 0.0.0.0:8000
release: cd volleyball_site && python manage.py migrate --noinput && python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123'); print('Admin account ready')"
