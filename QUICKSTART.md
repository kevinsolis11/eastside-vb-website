# Eastside VB Website - Deployment Quick Start

## 🚀 Go Live in 5 Steps

### For Local Testing (macOS/Linux)

```bash
# 1. Create virtualenv and install
python3 -m venv .venv
.venv/bin/python -m pip install -r volleyball_site/requirements.txt

# 2. Run migrations
.venv/bin/python volleyball_site/manage.py migrate

# 3. Create a test access code
.venv/bin/python volleyball_site/manage.py shell -c "from team.models import AccessCode; ac=AccessCode.generate(role='player'); print(f'Access Code: {ac.code}')"

# 4. Start all services (requires tmux)
./scripts/tmux_start.sh

# 5. Visit http://127.0.0.1:8000/
```

### For Production Deployment

Copy the entire repo to your server and run:

```bash
# SSH to server
ssh user@server.com
cd /path/to/eastside-vb-website

# Run the one-command deploy (requires sudo)
sudo ./scripts/deploy.sh --user volleyball --group volleyball

# View logs
tail -f logs/*.log
```

For detailed instructions, see [PRODUCTION_DEPLOY.md](PRODUCTION_DEPLOY.md).

## 📋 What's Included

- **Django 6.0** web framework with player signup & access codes
- **Celery** background task queue for sending invite emails
- **Redis** message broker
- **systemd** service units for production deployment
- **tmux** with log file support for development
- **Nginx** reverse proxy configuration example
- **Docker Compose** alternative deployment method

## 🔑 Key Features

✅ Access code-based player signup  
✅ Expiring invite codes with email binding  
✅ Async invite emails via Celery  
✅ Periodic cleanup of expired codes  
✅ Health check endpoint (`/healthz/`)  
✅ Admin interface for code management  
✅ Comprehensive logs and systemd integration  
✅ Production-ready with HTTPS support  

## 📁 Project Structure

```
.
├── volleyball_site/          # Django project
│   ├── team/                 # Player & access code app
│   ├── manage.py
│   ├── requirements.txt
│   └── settings.py
├── scripts/
│   ├── deploy.sh             # One-command production deploy
│   ├── tmux_start.sh         # Local dev tmux session
│   └── tmux_wrapper.sh       # Production tmux wrapper with logs
├── deployment/
│   ├── evb-tmux.service      # Systemd unit (basic)
│   ├── evb-tmux-logs.service # Systemd unit (with file logging)
│   ├── install_systemd.sh    # Service installer
│   └── volleyball_site.env.example
├── PRODUCTION_DEPLOY.md      # Full deployment guide
└── README.md
```

## 🔧 Configuration

### Environment Variables
Copy `deployment/volleyball_site.env.example` to `/etc/default/volleyball_site.env`:

```bash
APP_ROOT=/home/volleyball/eastside_vb_website
VENV_PATH=$APP_ROOT/.venv
TMUX_SESSION=evb
LOG_DIR=$APP_ROOT/logs
```

### Django Settings
Edit `volleyball_site/settings.py`:
- `ALLOWED_HOSTS` — add your domain
- `SECRET_KEY` — set a strong random key
- `EMAIL_*` — configure SMTP for sending invites
- `CELERY_BROKER_URL` — set to your Redis instance

## 📊 Services

| Service | Port | Purpose |
|---------|------|---------|
| Django Dev Server | 8000 | Web application |
| Celery Worker | — | Background tasks |
| Celery Beat | — | Scheduled tasks |
| Redis (optional) | 6379 | Message broker |
| Nginx (optional) | 80/443 | Reverse proxy |

## 🪵 Logs

**Development (tmux session):**
```bash
./scripts/tmux_start.sh
# Panes: web (left), worker (right), beat (bottom-left)
```

**Production (file logs):**
```bash
tail -f logs/web.log
tail -f logs/celery-worker.log
tail -f logs/celery-beat.log
```

**Systemd journal:**
```bash
sudo journalctl -u evb-tmux-logs.service -f
```

## ✅ Verification

```bash
# Check web server
curl http://127.0.0.1:8000/healthz/

# Check processes
pgrep -f runserver
pgrep -f "celery.*worker"
pgrep -f "celery.*beat"

# Check systemd services
sudo systemctl status evb-tmux-logs.service
```

## 🐛 Troubleshooting

**Connection refused:**
```bash
tail logs/web.log
sudo journalctl -u evb-tmux-logs.service -n 50
```

**Celery not processing tasks:**
```bash
tail logs/celery-worker.log
redis-cli ping  # Check Redis
```

**Emails not sending:**
```bash
# Test in shell
.venv/bin/python volleyball_site/manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

## 📚 More Info

- [Full Production Deployment Guide](PRODUCTION_DEPLOY.md)
- [Deployment README](DEPLOYMENT.md)
- Django Admin: `http://127.0.0.1:8000/admin/`
- Player Access Codes: Admin > Team > Access Codes

---

**Ready to deploy?** Run:
```bash
sudo ./scripts/deploy.sh
```

Questions? Check the logs!
