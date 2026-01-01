web: cd volleyball_site && gunicorn volleyball_site.wsgi --bind 0.0.0.0:8000
release: cd volleyball_site && python manage.py migrate --noinput
worker: cd volleyball_site && celery -A volleyball_site worker -l info --concurrency=2 --max-tasks-per-child=1000
