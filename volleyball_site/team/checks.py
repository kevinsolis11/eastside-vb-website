"""Django startup checks to validate email configuration."""
from django.core.checks import Warning, register
from django.conf import settings


@register()
def check_email_configuration(app_configs, **kwargs):
    """
    Check if email is properly configured on production.
    Shows a clear warning if email won't work.
    Uses Warning instead of Error so deployment isn't blocked.
    """
    warnings = []
    
    # Only check in production (not DEBUG mode)
    if getattr(settings, 'DEBUG', False):
        return warnings  # Skip checks in development
    
    email_host = getattr(settings, 'EMAIL_HOST', '').strip()
    email_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
    
    # Check if email is configured (use Warning level, not Error, so it doesn't block deploy)
    if not email_host or email_host == 'localhost':
        warnings.append(
            Warning(
                'Email HOST not configured or set to localhost',
                hint='Set EMAIL_HOST environment variable (e.g., smtp.gmail.com)',
                id='email.W001',
            )
        )
    
    if not email_user:
        warnings.append(
            Warning(
                'Email USERNAME/USER not configured',
                hint='Set EMAIL_HOST_USER environment variable (e.g., your-email@gmail.com)',
                id='email.W002',
            )
        )
    
    if not email_password:
        warnings.append(
            Warning(
                'Email PASSWORD not configured',
                hint='Set EMAIL_HOST_PASSWORD environment variable',
                id='email.W003',
            )
        )
    
    if warnings:
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
    
    return warnings
