#!/bin/bash
# Setup Nginx and Let's Encrypt HTTPS for Eastside VB Website
# Usage: sudo ./deployment/setup_https.sh your-domain.com [email@example.com]

set -e

if [ "$#" -lt 1 ]; then
  echo "Usage: sudo $0 <domain> [email]"
  echo "Example: sudo $0 volleyball.example.com admin@example.com"
  exit 1
fi

DOMAIN="$1"
EMAIL="${2:-admin@$DOMAIN}"
APP_ROOT="/home/volleyball/eastside-vb-website"

echo "Setting up HTTPS for $DOMAIN (email: $EMAIL)"

# Step 1: Install Nginx if not present
if ! command -v nginx >/dev/null 2>&1; then
  echo "Installing Nginx..."
  apt-get update
  apt-get install -y nginx
fi

# Step 2: Install Certbot
if ! command -v certbot >/dev/null 2>&1; then
  echo "Installing Certbot..."
  apt-get install -y certbot python3-certbot-nginx
fi

# Step 3: Create Certbot verification directory
mkdir -p /var/www/certbot

# Step 4: Create Nginx config from template
echo "Creating Nginx configuration..."
cp "$APP_ROOT/deployment/nginx.conf" /etc/nginx/sites-available/volleyball_site
sed -i "s/your-domain\.com/$DOMAIN/g" /etc/nginx/sites-available/volleyball_site
sed -i "s|/home/volleyball/eastside-vb-website|$APP_ROOT|g" /etc/nginx/sites-available/volleyball_site

# Step 5: Enable site
if [ ! -L /etc/nginx/sites-enabled/volleyball_site ]; then
  ln -s /etc/nginx/sites-available/volleyball_site /etc/nginx/sites-enabled/
fi

# Step 6: Test and reload Nginx
echo "Testing Nginx configuration..."
nginx -t
echo "Reloading Nginx..."
systemctl reload nginx

# Step 7: Get SSL certificate
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  echo "Obtaining Let's Encrypt certificate for $DOMAIN..."
  certbot certonly --webroot -w /var/www/certbot -d "$DOMAIN" -d "www.$DOMAIN" \
    --email "$EMAIL" --agree-tos --no-eff-email --non-interactive
else
  echo "Certificate already exists for $DOMAIN"
fi

# Step 8: Create certbot renewal timer
echo "Setting up automatic certificate renewal..."
systemctl enable certbot.timer || true
systemctl start certbot.timer || true

# Step 9: Final Nginx reload with SSL
echo "Reloading Nginx with SSL..."
systemctl reload nginx

# Step 10: Verify
echo ""
echo "✓ Setup complete!"
echo ""
echo "Verify SSL certificate:"
echo "  curl -I https://$DOMAIN"
echo ""
echo "Check certificate expiration:"
echo "  sudo certbot certificates"
echo ""
echo "Force renewal (for testing):"
echo "  sudo certbot renew --dry-run"
echo ""
echo "View Nginx logs:"
echo "  tail -f /var/log/nginx/volleyball_site_access.log"
echo "  tail -f /var/log/nginx/volleyball_site_error.log"
