# Production Configuration & Setup Guide

## Quick Setup Summary

After running `sudo ./scripts/deploy.sh`, follow these 5 steps to complete production setup:

---

## 1️⃣ Configure Nginx Reverse Proxy

### Install Nginx
```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### Setup Nginx
```bash
# Copy template and customize
sudo cp deployment/nginx.conf /etc/nginx/sites-available/volleyball_site

# Edit domain names
sudo nano /etc/nginx/sites-available/volleyball_site

# Enable the site
sudo ln -s /etc/nginx/sites-available/volleyball_site /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### Verify Nginx is working
```bash
curl -I http://127.0.0.1
# Should see Nginx response
```

---

## 2️⃣ Set Up HTTPS with Let's Encrypt

### Automated Setup (Recommended)
```bash
sudo ./deployment/setup_https.sh your-domain.com admin@example.com
```

This will:
- Install Certbot
- Generate SSL certificate
- Update Nginx configuration
- Enable auto-renewal

### Manual Setup
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --webroot -w /var/www/certbot \
  -d your-domain.com -d www.your-domain.com \
  --email admin@example.com --agree-tos --non-interactive

# Update Nginx (see deployment/nginx.conf for template)
# Edit /etc/nginx/sites-available/volleyball_site
sudo nano /etc/nginx/sites-available/volleyball_site

# Test and reload
sudo nginx -t
sudo systemctl reload nginx

# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Verify HTTPS
```bash
curl -I https://your-domain.com
# Should see 200 OK with HTTPS

# Check certificate
sudo certbot certificates

# Test renewal (dry-run, doesn't actually renew)
sudo certbot renew --dry-run
```

---

## 3️⃣ Update Django Settings for Your Domain

### Create Production Settings
```bash
# Copy template
cp volleyball_site/settings_prod.py volleyball_site/settings_prod.py.bak

# Edit environment variables
sudo nano /etc/default/volleyball_site.env
```

### Add Required Environment Variables
```bash
# Add these to /etc/default/volleyball_site.env:
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_DEBUG=False
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

### Generate Secret Key
```bash
# Generate a random secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Restart Services
```bash
sudo systemctl restart evb-tmux-logs.service

# Verify
curl https://your-domain.com/healthz/
# Should return: {"status": "OK"}
```

---

## 4️⃣ Configure SMTP for Email Sending

### Interactive Setup
```bash
# Gmail (easiest)
sudo ./deployment/setup_smtp.sh gmail

# SendGrid
sudo ./deployment/setup_smtp.sh sendgrid

# AWS SES
sudo ./deployment/setup_smtp.sh ses

# Custom SMTP
sudo ./deployment/setup_smtp.sh custom
```

### Gmail Configuration (Step-by-step)
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character App Password
4. Run: `sudo ./deployment/setup_smtp.sh gmail`
5. Enter your Gmail address and App Password

### SendGrid Configuration
1. Sign up at https://sendgrid.com
2. Create API key in Settings > API Keys > Create API Key
3. Run: `sudo ./deployment/setup_smtp.sh sendgrid` [from-email@your-domain.com](mailto:from-email@your-domain.com)
4. Enter your API key

### AWS SES Configuration
1. Verify sender email in AWS SES console
2. Create SMTP credentials in Email Sending > Account Dashboard
3. Run: `sudo ./deployment/setup_smtp.sh ses`
4. Enter credentials

### Test Email Configuration
```bash
cd /home/volleyball/eastside-vb-website

# Test email sending
.venv/bin/python volleyball_site/manage.py shell < deployment/test_email.py

# Should see:
# ✓ Email sent successfully
# ✓ HTML email sent successfully
```

### Troubleshooting Email
```bash
# Check environment variables
sudo cat /etc/default/volleyball_site.env | grep EMAIL

# Test in Django shell
.venv/bin/python volleyball_site/manage.py shell
>>> from django.core.mail import get_connection
>>> conn = get_connection()
>>> conn.open()  # Will raise exception if fails
>>> conn.close()

# Check logs
tail -f logs/django.log
tail -f logs/celery-worker.log
```

---

## 5️⃣ Set Up Automated Backups

### Enable Backup Timer
```bash
# Copy backup script
sudo cp deployment/backup.sh /opt/volleyball_site/backup.sh
sudo chmod +x /opt/volleyball_site/backup.sh

# Install systemd timer
sudo cp deployment/backup.service /etc/systemd/system/
sudo cp deployment/backup.timer /etc/systemd/system/

# Enable backup timer
sudo systemctl daemon-reload
sudo systemctl enable backup.timer
sudo systemctl start backup.timer

# Verify timer is active
sudo systemctl list-timers | grep backup
```

### Manual Backup
```bash
cd /home/volleyball/eastside-vb-website

# Run backup immediately
./deployment/backup.sh

# Compress backup
./deployment/backup.sh true

# Check backups
ls -lah backups/
```

### Backup to AWS S3 (Optional)
```bash
# Install AWS CLI
sudo apt-get install -y awscli

# Configure AWS credentials
aws configure

# Create S3 bucket
aws s3 mb s3://volleyball-site-backups

# Enable backup to S3
export S3_BUCKET=volleyball-site-backups
./deployment/backup.sh true true
```

### Restore from Backup
```bash
# List available backups
ls -la backups/database/

# Restore database
cp backups/database/db_TIMESTAMP.sqlite3 volleyball_site/db.sqlite3

# Restore media
tar xzf backups/media/media_TIMESTAMP.tar.gz -C volleyball_site/

# Restart application
sudo systemctl restart evb-tmux-logs.service
```

### Backup Schedule
- **Default**: Daily at 2:00 AM
- **Retention**: 30 days (older backups auto-deleted)
- **Location**: `/home/volleyball/eastside-vb-website/backups/`

---

## ✅ Complete Production Checklist

- [ ] Domain registered and pointing to server
- [ ] Nginx installed and configured
- [ ] HTTPS certificate obtained and auto-renewal enabled
- [ ] Django settings updated with domain and secret key
- [ ] SMTP configured and tested
- [ ] Automated backups enabled
- [ ] Services running: `sudo systemctl status evb-tmux-logs.service`
- [ ] Health check responding: `curl https://your-domain.com/healthz/`
- [ ] Test user signup flow
- [ ] Test invite email sending
- [ ] Test access code generation
- [ ] Monitor logs: `tail -f logs/*.log`
- [ ] Set up monitoring/alerting (optional)

---

## 🔒 Security Hardening (Optional)

### Set up Firewall
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Disable Root Login
```bash
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### Enable Automatic Security Updates
```bash
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Set up Fail2Ban
```bash
sudo apt-get install -y fail2ban

# Create config
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local  # Enable sshd jails

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📊 Monitoring & Alerts

### View Logs
```bash
# All logs
tail -f /home/volleyball/eastside-vb-website/logs/*.log

# Nginx
tail -f /var/log/nginx/volleyball_site_*.log

# Systemd journal
sudo journalctl -u evb-tmux-logs.service -f
```

### Check Service Status
```bash
# All services
sudo systemctl status evb-tmux-logs.service

# Individual checks
pgrep -f runserver && echo "✓ Web" || echo "✗ Web"
pgrep -f "celery.*worker" && echo "✓ Worker" || echo "✗ Worker"
pgrep -f "celery.*beat" && echo "✓ Beat" || echo "✗ Beat"
```

### Set Up Email Alerts (Optional)
```bash
# Install postfix for system emails
sudo apt-get install -y postfix

# Configure Celery task notifications in settings.py
```

---

## 🔄 Maintenance

### Weekly
- [ ] Check disk space: `df -h`
- [ ] Review error logs: `tail logs/django.log`
- [ ] Verify backups exist: `ls backups/`

### Monthly
- [ ] Check for updates: `sudo apt update && apt upgrade -y`
- [ ] Rotate access codes if needed
- [ ] Review user activity in admin
- [ ] Test backup restoration

### Quarterly
- [ ] Review and update security settings
- [ ] Update Django and dependencies: `.venv/bin/pip install --upgrade -r requirements.txt`
- [ ] Optimize database: `.venv/bin/python manage.py optimize`

---

## 📞 Support & Troubleshooting

### Common Issues

**Nginx can't connect to Django:**
```bash
# Check if Django is listening
netstat -tlnp | grep 8000

# Check logs
tail -50 logs/web.log
sudo journalctl -u evb-tmux-logs.service -n 50
```

**SSL certificate errors:**
```bash
# Check certificate
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check Nginx logs
tail /var/log/nginx/volleyball_site_error.log
```

**Email not sending:**
```bash
# Test SMTP connection
openssl s_client -connect smtp.gmail.com:587 -starttls smtp

# Check Celery logs
tail logs/celery-worker.log
```

**High disk usage:**
```bash
# Check what's using space
du -sh /*
du -sh /home/volleyball/eastside-vb-website/*

# Clean old backups manually
find /home/volleyball/eastside-vb-website/backups -mtime +30 -delete
```

---

## Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
