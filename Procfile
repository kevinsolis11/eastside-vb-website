web: cd volleyball_site && gunicorn volleyball_site.wsgi --bind 0.0.0.0:8000
release: cd volleyball_site && python manage.py migrate --noinput && echo "from django.contrib.auth.models import User; User.objects.filter(username='kevinsolis').exists() or User.objects.create_superuser('kevinsolis', 'kevinsolis@example.com', 'admin123')" | python manage.py shell
