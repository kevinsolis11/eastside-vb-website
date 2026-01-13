"""Management command to create a test coach account."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a test coach account'

    def handle(self, *args, **options):
        username = 'testcoach'
        password = 'coach123'
        email = 'testcoach@eastsidevolleyball.com'

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Coach account updated: {username}'))
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.first_name = 'Test'
            user.last_name = 'Coach'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Coach account created: {username}'))

        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
