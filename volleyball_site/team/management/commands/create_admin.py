from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create default admin account if it does not exist'

    def handle(self, *args, **options):
        username = 'kevinsolis'
        email = 'kevinsolis@example.com'
        password = 'admin123'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {username}')
            )
        else:
            # Update password in case it changed
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Admin user {username} already exists, password updated')
            )
