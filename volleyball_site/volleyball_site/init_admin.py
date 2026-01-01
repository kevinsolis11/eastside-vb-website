"""
Django settings to auto-create admin user
"""
import os

# This gets imported at the end of settings.py
def ensure_admin_exists():
    """Ensure admin user exists (called on app startup)"""
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(username='kevinsolis').exists():
            User.objects.create_superuser(
                'kevinsolis',
                'kevinsolis@example.com',
                'admin123'
            )
    except Exception as e:
        # Silently fail if DB not ready yet
        pass


# Auto-create admin on import if in production
if os.environ.get('RAILWAY_ENVIRONMENT'):
    ensure_admin_exists()
