# Deployment notes (systemd + Celery)

Recommended environment variables (set in `.env` or systemd unit):

- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_DEBUG` - `True` or `False`
- `DJANGO_ALLOWED_HOSTS` - comma-separated hosts
- `DEFAULT_FROM_EMAIL` - e.g. `noreply@example.com`
- `DEFAULT_FROM_NAME` - display name for outgoing mail (e.g. `Eastside VB`)
- `DEFAULT_REPLY_TO` - optional reply-to address
- `CELERY_BROKER_URL` - e.g. `redis://redis:6379/0`

Systemd unit examples are in `deployment/`:

- `deployment/gunicorn.service` — gunicorn web service
- `deployment/celery.service` — Celery worker
- `deployment/celery-beat.service` — Celery Beat scheduler

Install and enable (example):

```bash
sudo cp deployment/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn.service celery.service celery-beat.service
```

The Docker image entrypoint runs migrations and creates the periodic cleanup task on start; adjust if you prefer migrations as a separate init task.

Systemd service setup (example)
-------------------------------

1. Copy the example env file and edit values:

```bash
sudo cp deployment/volleyball_site.env.example /etc/default/volleyball_site.env
sudo editor /etc/default/volleyball_site.env    # replace values
```

2. Copy systemd unit files and enable services:

```bash
sudo cp deployment/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn.service
sudo systemctl enable --now celery.service
sudo systemctl enable --now celery-beat.service
```

3. Check status and logs:

```bash
systemctl status gunicorn.service --no-pager
journalctl -u gunicorn.service -b --no-pager | tail -n 200

systemctl status celery.service --no-pager
journalctl -u celery.service -b --no-pager | tail -n 200

systemctl status celery-beat.service --no-pager
journalctl -u celery-beat.service -b --no-pager | tail -n 200
```

4. If you run into permission or file issues, ensure the `WorkingDirectory` and `ExecStart` paths in the unit files match your server layout and that the `User` has access to the project and the `.venv`.

Note: the example env file is located at `deployment/volleyball_site.env.example`.
