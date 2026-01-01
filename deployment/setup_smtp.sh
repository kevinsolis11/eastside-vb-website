#!/bin/bash
# Setup SMTP email configuration for Eastside VB Website
# Supports: Gmail, SendGrid, AWS SES, or custom SMTP
# Usage: ./deployment/setup_smtp.sh <provider> [options]

set -e

PROVIDER="${1:-gmail}"
ENV_FILE="/etc/default/volleyball_site.env"

echo "Setting up email configuration for: $PROVIDER"
echo ""

case "$PROVIDER" in
  gmail)
    echo "Gmail Configuration:"
    echo "1. Enable 2-Factor Authentication on your Gmail account"
    echo "2. Create an App Password: https://myaccount.google.com/apppasswords"
    echo "3. Copy the 16-character App Password"
    echo ""
    read -p "Enter Gmail address: " EMAIL_HOST_USER
    read -sp "Enter Gmail App Password: " EMAIL_HOST_PASSWORD
    echo ""
    
    EMAIL_HOST="smtp.gmail.com"
    EMAIL_PORT="587"
    EMAIL_USE_TLS="True"
    DEFAULT_FROM_EMAIL="$EMAIL_HOST_USER"
    ;;
    
  sendgrid)
    echo "SendGrid Configuration:"
    echo "1. Sign up at https://sendgrid.com"
    echo "2. Create API key: Settings > API Keys > Create API Key"
    echo "3. Copy the API key"
    echo ""
    read -sp "Enter SendGrid API Key: " SENDGRID_API_KEY
    echo ""
    
    EMAIL_HOST="smtp.sendgrid.net"
    EMAIL_PORT="587"
    EMAIL_USE_TLS="True"
    EMAIL_HOST_USER="apikey"
    EMAIL_HOST_PASSWORD="$SENDGRID_API_KEY"
    DEFAULT_FROM_EMAIL="${2:-noreply@example.com}"
    ;;
    
  ses)
    echo "AWS SES Configuration:"
    echo "1. Verify sender email in AWS SES console"
    echo "2. Create SMTP credentials: Email Sending > Account Dashboard > Create SMTP credentials"
    echo ""
    read -p "Enter AWS SES region (default: us-east-1): " AWS_REGION
    AWS_REGION="${AWS_REGION:-us-east-1}"
    read -p "Enter SMTP username: " EMAIL_HOST_USER
    read -sp "Enter SMTP password: " EMAIL_HOST_PASSWORD
    echo ""
    
    EMAIL_HOST="email-smtp.${AWS_REGION}.amazonaws.com"
    EMAIL_PORT="587"
    EMAIL_USE_TLS="True"
    DEFAULT_FROM_EMAIL="${2:-noreply@example.com}"
    ;;
    
  custom)
    echo "Custom SMTP Configuration:"
    read -p "Enter SMTP hostname: " EMAIL_HOST
    read -p "Enter SMTP port (default: 587): " EMAIL_PORT
    EMAIL_PORT="${EMAIL_PORT:-587}"
    read -p "Use TLS? (true/false, default: true): " EMAIL_USE_TLS
    EMAIL_USE_TLS="${EMAIL_USE_TLS:-true}"
    read -p "Enter SMTP username: " EMAIL_HOST_USER
    read -sp "Enter SMTP password: " EMAIL_HOST_PASSWORD
    echo ""
    read -p "Enter 'From' email address: " DEFAULT_FROM_EMAIL
    ;;
    
  *)
    echo "Unknown provider: $PROVIDER"
    echo "Supported: gmail, sendgrid, ses, custom"
    exit 1
    ;;
esac

echo ""
echo "Email configuration:"
echo "  Host: $EMAIL_HOST"
echo "  Port: $EMAIL_PORT"
echo "  Use TLS: $EMAIL_USE_TLS"
echo "  From Email: $DEFAULT_FROM_EMAIL"
echo ""

# Update environment file
echo "Updating $ENV_FILE..."
if [ ! -f "$ENV_FILE" ]; then
  sudo touch "$ENV_FILE"
fi

# Use a temp file to avoid partial writes
TEMP_ENV=$(mktemp)
cp "$ENV_FILE" "$TEMP_ENV" 2>/dev/null || true

# Remove existing email settings
grep -v "^EMAIL_\|^DEFAULT_FROM\|^DEFAULT_REPLY" "$TEMP_ENV" > "$TEMP_ENV.new" || true

# Add new settings
cat >> "$TEMP_ENV.new" <<EOF
EMAIL_HOST=$EMAIL_HOST
EMAIL_PORT=$EMAIL_PORT
EMAIL_USE_TLS=$EMAIL_USE_TLS
EMAIL_HOST_USER=$EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL
DEFAULT_FROM_NAME=Eastside Volleyball
DEFAULT_REPLY_TO=$DEFAULT_FROM_EMAIL
EOF

sudo mv "$TEMP_ENV.new" "$ENV_FILE"
sudo chmod 640 "$ENV_FILE"

echo "✓ Email configuration saved"
echo ""
echo "Next steps:"
echo "1. Test email sending:"
echo "   cd /home/volleyball/eastside-vb-website"
echo "   .venv/bin/python volleyball_site/manage.py shell < deployment/test_email.py"
echo ""
echo "2. Restart Celery worker:"
echo "   sudo systemctl restart evb-tmux-logs.service"
echo ""
echo "3. Test invite email generation in Django admin"
