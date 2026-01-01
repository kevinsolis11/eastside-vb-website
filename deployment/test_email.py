#!/usr/bin/env python
# Test email configuration
# Usage: .venv/bin/python volleyball_site/manage.py shell < deployment/test_email.py

import os
from django.core.mail import send_mail
from django.template.loader import render_to_string

print("Testing Django email configuration...")
print(f"EMAIL_BACKEND: {os.getenv('EMAIL_BACKEND', 'SMTP')}")
print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST')}")
print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT')}")
print(f"EMAIL_USE_TLS: {os.getenv('EMAIL_USE_TLS')}")
print(f"DEFAULT_FROM_EMAIL: {os.getenv('DEFAULT_FROM_EMAIL')}")
print()

# Test 1: Simple text email
print("Test 1: Sending simple test email...")
try:
    result = send_mail(
        subject='Eastside VB Email Test',
        message='This is a test email from the Django application.',
        from_email=os.getenv('DEFAULT_FROM_EMAIL'),
        recipient_list=['test@example.com'],
        fail_silently=False,
    )
    print(f"✓ Email sent successfully (result: {result})")
except Exception as e:
    print(f"✗ Failed to send email: {e}")

# Test 2: HTML email (like invite)
print()
print("Test 2: Sending HTML invite-style email...")
try:
    from team.models import AccessCode
    
    # Create a test code
    access_code_obj = AccessCode.generate(role='player')
    
    context = {
        'code': access_code_obj,
        'site_url': 'https://your-domain.com',
        'signup_url': f'https://your-domain.com/signup/?code={getattr(access_code_obj, "code", "TEST-CODE")}',
    }
    
    html_message = render_to_string('emails/invite_email.html', context)
    text_message = render_to_string('emails/invite_email.txt', context)
    
    result = send_mail(
        subject='You are invited to join Eastside Volleyball',
        message=text_message,
        from_email=os.getenv('DEFAULT_FROM_EMAIL'),
        recipient_list=['test@example.com'],
        html_message=html_message,
        fail_silently=False,
    )
    print(f"✓ HTML email sent successfully (result: {result})")
    print(f"  (This code will expire in 7 days)")
    
except Exception as e:
    print(f"✗ Failed to send HTML email: {e}")

print()
print("Email testing complete!")
print()
print("If emails failed:")
print("  1. Check credentials in /etc/default/volleyball_site.env")
print("  2. Verify firewall allows SMTP (port 587)")
print("  3. Check Django logs: tail -f logs/django.log")
print("  4. Run: .venv/bin/python volleyball_site/manage.py shell")
print("     from django.core.mail import get_connection")
print("     conn = get_connection()")
print("     conn.open()  # Will raise exception if connection fails")
