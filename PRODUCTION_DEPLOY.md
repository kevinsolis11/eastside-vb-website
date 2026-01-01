# Production Deployment Guide

## Prerequisites

- Ubuntu 20.04+ or similar Linux (systemd-based)
- Python 3.9+
- git
- tmux installed (`sudo apt install tmux`)
- Nginx for reverse proxy (optional but recommended)

## Step 1: Clone & Prepare

```bash
# SSH into your server
ssh user@server

# Clone the repo
cd /home/volleyball
git clone https://github.com/your-org/eastside-vb-website.git
cd eastside-vb-website

# Create virtualenv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -r volleyball_site/requirements.txt

# Create a dedicated user (optional but recommended)
sudo useradd -m -s /bin/bash volleyball || true
sudo chown -R volleyball:volleyball /home/volleyball/eastside-vb-website
```

## Step 2: Database & Static Files

```bash
# Run migrations
.venv/bin/python volleyball_site/manage.py migrate --noinput

# Collect static files
.venv/bin/python volleyball_site/manage.py collectstatic --noinput

# Create superuser (one-time)
.venv/bin/python volleyball_site/manage.py createsuperuser

# Create periodic cleanup task
.venv/bin/python volleyball_site/manage.py create_cleanup_periodic
```

## Step 3: Copy & Configure Environment

```bash
# Copy env template to /etc/default
sudo cp deployment/volleyball_site.env.example /etc/default/volleyball_site.env

# Edit the env file for your server
sudo nano /etc/default/volleyball_site.env

# Expected values (edit as needed):
# APP_ROOT=/home/volleyball/eastside-vb-website
# VENV_PATH=/home/volleyball/eastside-vb-website/.venv
# TMUX_SESSION=evb
# LOG_DIR=/home/volleyball/eastside-vb-website/logs
```

## Step 4: Install Systemd Services

```bash
# Run installer with --user and --group flags
sudo ./deployment/install_systemd.sh --force --user volleyball --group volleyball

# Verify all services are enabled
sudo systemctl list-unit-files | grep evb-tmux
sudo systemctl list-unit-files | grep gunicorn
```

## Step 5: Start Services

```bash
# Start the log-based tmux unit (recommended)
sudo systemctl start evb-tmux-logs.service

# Verify status
sudo systemctl status evb-tmux-logs.service

# Or use the original (no logs to files)
sudo systemctl start evb-tmux.service
sudo systemctl status evb-tmux.service
```

## Step 6: Verify Services Running

```bash
# Check processes
pgrep -f "runserver" && echo "✓ Web server running"
pgrep -f "celery.*worker" && echo "✓ Celery worker running"
pgrep -f "celery.*beat" && echo "✓ Celery beat running"

# Check web endpoint
curl -s http://127.0.0.1:8000/healthz/ | grep -q "OK" && echo "✓ Healthcheck OK"

# Tail logs (if using evb-tmux-logs)
tail -f /home/volleyball/eastside-vb-website/logs/web.log
tail -f /home/volleyball/eastside-vb-website/logs/celery-worker.log
tail -f /home/volleyball/eastside-vb-website/logs/celery-beat.log
```

## Step 7: Configure Nginx (Optional but Recommended)

Create `/etc/nginx/sites-available/volleyball_site`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/volleyball/eastside-vb-website/volleyball_site/staticfiles/;
    }

    location /media/ {
        alias /home/volleyball/eastside-vb-website/volleyball_site/media/;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/volleyball_site /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 8: Enable HTTPS (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Step 9: Monitor & Troubleshoot

### Check service status
```bash
sudo systemctl status evb-tmux-logs.service
sudo systemctl status evb-tmux.service
```

### View logs
```bash
# From log files
tail -f /home/volleyball/eastside-vb-website/logs/*.log

# From systemd journal
sudo journalctl -u evb-tmux-logs.service -f
sudo journalctl -u evb-tmux.service -f
```

### Restart services
```bash
sudo systemctl restart evb-tmux-logs.service

# Or kill and restart via systemd
sudo systemctl stop evb-tmux-logs.service
sudo systemctl start evb-tmux-logs.service
```

### Test email invites
```bash
cd /home/volleyball/eastside-vb-website
.venv/bin/python volleyball_site/manage.py shell

# In the shell:
from team.models import AccessCode
code = AccessCode.generate(role='player', expires_at=None, allowed_email='test@example.com')
print(f"Code: {code.code}")

# Check if invite email task was enqueued
from celery.result import AsyncResult
# Or simply wait and check celery logs
```

### Test cleanup task
```bash
.venv/bin/python volleyball_site/manage.py cleanup_accesscodes --dry-run
.venv/bin/python volleyball_site/manage.py cleanup_accesscodes
```

## Step 10: Backup & Maintenance

```bash
# Backup database daily
0 2 * * * /home/volleyball/eastside-vb-website/.venv/bin/python \
  /home/volleyball/eastside-vb-website/volleyball_site/manage.py dbbackup -z

# Log rotation (create /etc/logrotate.d/volleyball_site)
/home/volleyball/eastside-vb-website/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
    postrotate
        sudo systemctl reload evb-tmux-logs.service > /dev/null 2>&1 || true
    endscript
}
```

## Production Checklist

- [ ] Clone repo and install dependencies
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create superuser
- [ ] Create periodic task (create_cleanup_periodic)
- [ ] Copy and edit `/etc/default/volleyball_site.env`
- [ ] Run install_systemd.sh with --user and --group
- [ ] Start systemd services
- [ ] Verify web, worker, and beat are running
- [ ] Test healthcheck endpoint
- [ ] Test invite email sending
- [ ] Configure Nginx reverse proxy
- [ ] Set up HTTPS with Let's Encrypt
- [ ] Set up log rotation
- [ ] Enable systemd services on boot (`systemctl enable`)
- [ ] Set up database backups
- [ ] Monitor logs for errors

## Troubleshooting

### "Connection refused" on port 8000
- Check if web server is running: `pgrep -f runserver`
- Check systemd journal: `sudo journalctl -u evb-tmux-logs.service -n 50`
- Check log files: `tail -f /home/volleyball/eastside-vb-website/logs/web.log`

### Celery worker not processing tasks
- Check if worker is running: `pgrep -f "celery.*worker"`
- Check Redis is accessible: `redis-cli ping`
- Check logs: `tail -f /home/volleyball/eastside-vb-website/logs/celery-worker.log`

### Emails not sending
- Check Celery task logs
- Verify email settings in `volleyball_site/settings.py`
- Test: `python manage.py shell` → `from django.core.mail import send_mail; send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])`

### Permission errors
- Ensure volleyball user owns the directory: `sudo chown -R volleyball:volleyball /home/volleyball/eastside-vb-website`
- Ensure logs directory is writable: `sudo chmod 755 /home/volleyball/eastside-vb-website/logs`

## Rollback

If something breaks:
```bash
# Stop services
sudo systemctl stop evb-tmux-logs.service

# Revert last git commit
git revert HEAD

# Run migrations if schema changed
.venv/bin/python volleyball_site/manage.py migrate

# Restart
sudo systemctl start evb-tmux-logs.service
```

## Support

For issues, check:
1. systemd journal: `sudo journalctl -u evb-tmux-logs.service -n 100`
2. Log files: `tail -100 /home/volleyball/eastside-vb-website/logs/*.log`
3. Database: Run `./manage.py dbshell` to inspect tables
4. Celery: Check Redis connection and Celery tasks in admin interface
