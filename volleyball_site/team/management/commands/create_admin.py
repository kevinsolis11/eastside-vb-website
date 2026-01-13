"""
Management command to create or reset the admin superuser.
This runs during Railway deployment to ensure admin access.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or reset admin superuser for Railway deployment'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@eastsidevb.com'
        password = 'admin123'
        
        # Check if admin user exists
        try:
            user = User.objects.get(username=username)
            # Reset the password
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Admin user "{username}" password reset to "{password}"'))
        except User.DoesNotExist:
            # Create the admin user
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Admin superuser "{username}" created with password "{password}"'))
        
        # Also ensure coach user is a superuser
        try:
            coach = User.objects.get(username='coach')
            coach.is_superuser = True
            coach.is_staff = True
            coach.set_password('coach123')
            coach.save()
            self.stdout.write(self.style.SUCCESS('✅ Coach user upgraded to superuser'))
        except User.DoesNotExist:
            pass
        
        self.stdout.write(self.style.SUCCESS(f'''
========================================
🔐 ADMIN LOGIN CREDENTIALS:
   URL: /admin/
   Username: {username}
   Password: {password}
   
   OR use coach account:
   Username: coach
   Password: coach123
========================================
'''))
