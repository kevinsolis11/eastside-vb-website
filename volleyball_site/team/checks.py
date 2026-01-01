"""Django startup checks to validate email configuration."""
from django.core.checks import Error, register
from django.conf import settings


@register()
def check_email_configuration(app_configs, **kwargs):
    """
    Check if email is properly configured on production.
    Shows a clear warning if email won't work.
    """
    errors = []
    
    # Only check in production (not DEBUG mode)
    if getattr(settings, 'DEBUG', False):
        return errors  # Skip checks in development
    
    email_host = getattr(settings, 'EMAIL_HOST', '').strip()
    email_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
    
    # Check if email is configured
    if not email_host or email_host == 'localhost':
        errors.append(
            Error(
                'Email HOST not configured or set to localhost',
                hint='Set EMAIL_HOST environment variable (e.g., smtp.gmail.com)',
                id='email.E001',
            )
        )
    
    if not email_user:
        errors.append(
            Error(
                'Email USERNAME/USER not configured',
                hint='Set EMAIL_HOST_USER environment variable (e.g., your-email@gmail.com)',
                id='email.E002',
            )
        )
    
    if not email_password:
        errors.append(
            Error(
                'Email PASSWORD not configured',
                hint='Set EMAIL_HOST_PASSWORD environment variable',
                id='email.E003',
            )
        )
    
    if errors:
        print("\n" + "="*70)
        print("⚠️  EMAIL CONFIGURATION WARNING")
        print("="*70)
        print("Email is not properly configured on this server.")
        print("Coaches will NOT be able to send invite codes to players.")
        print("\nTo fix, set these environment variables:")
        print("  EMAIL_HOST=smtp.gmail.com")
        print("  EMAIL_HOST_USER=your-email@gmail.com")
        print("  EMAIL_HOST_PASSWORD=your-app-password")
        print("="*70 + "\n")
    
    return errors
