"""Management command to create a test coach account."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from team.models import PlayerProfile


class Command(BaseCommand):
    help = 'Create a test coach account'

    def handle(self, *args, **options):
        # Also reset the existing 'coach' account password
        try:
            coach_user = User.objects.get(username='coach')
            coach_user.set_password('coach123')
            coach_user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Reset password for coach account'))
        except User.DoesNotExist:
            pass
        
        username = 'testcoach'
        password = 'coach123'
        email = 'testcoach@eastsidevolleyball.com'

        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Test',
                'last_name': 'Coach',
                'is_staff': True,
                'is_active': True,
            }
        )
        
        if not created:
            # Update existing user
            user.set_password(password)
            user.is_staff = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Coach account updated: {username}'))
        else:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Coach account created: {username}'))

        # Create or update PlayerProfile
        profile, profile_created = PlayerProfile.objects.get_or_create(
            user=user,
            defaults={'position': 'Coach'}
        )
        
        if profile_created:
            self.stdout.write(self.style.SUCCESS(f'✅ PlayerProfile created for coach'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ PlayerProfile already exists'))

        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Has Profile: True')
