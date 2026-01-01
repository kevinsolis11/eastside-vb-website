import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from team.models import Player, PlayerProfile, PlayerStats


class Command(BaseCommand):
    help = 'Create a test player with stats for development/testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testplayer',
            help='Username for the test player (default: testplayer)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for the test player (default: testpass123)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Test',
            help='First name of the player (default: Test)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='Player',
            help='Last name of the player (default: Player)'
        )
        parser.add_argument(
            '--number',
            type=int,
            default=12,
            help='Jersey number (default: 12)'
        )
        parser.add_argument(
            '--position',
            type=str,
            default='Middle Blocker',
            help='Position (default: Middle Blocker)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        number = options['number']
        position = options['position']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists. Updating...'))
            user = User.objects.get(username=username)
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        else:
            # Create Django User
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created user "{username}"'))

        # Create or update Player
        player, created = Player.objects.update_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={
                'number': number,
                'position': position,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created player #{number} {first_name} {last_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated player #{number} {first_name} {last_name}'))

        # Create or update PlayerProfile
        profile, created = PlayerProfile.objects.update_or_create(
            user=user,
            defaults={
                'player': player,
                'position': position,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created player profile'))

        # Create or update PlayerStats with random data
        stats = {
            'kills': random.randint(100, 300),
            'blocks': random.randint(20, 80),
            'aces': random.randint(5, 25),
            'digs': random.randint(80, 200),
        }
        stats_obj, created = PlayerStats.objects.update_or_create(
            player=profile,
            defaults=stats
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created player stats'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated player stats'))

        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('TEST PLAYER CREATED SUCCESSFULLY!'))
        self.stdout.write('='*50)
        self.stdout.write(f'\nLogin Credentials:')
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'\nPlayer Info:')
        self.stdout.write(f'  Name:     #{number} {first_name} {last_name}')
        self.stdout.write(f'  Position: {position}')
        self.stdout.write(f'\nPlayer Stats:')
        self.stdout.write(f'  Kills:    {stats_obj.kills}')
        self.stdout.write(f'  Blocks:   {stats_obj.blocks}')
        self.stdout.write(f'  Aces:     {stats_obj.aces}')
        self.stdout.write(f'  Digs:     {stats_obj.digs}')
        self.stdout.write(f'\nURL: http://localhost:8000\n')
