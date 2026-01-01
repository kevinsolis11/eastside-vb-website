from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from team.models import AccessCode


class Command(BaseCommand):
    help = 'Cleanup old access codes: remove expired or used codes older than N days.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Delete codes older than this many days')

    def handle(self, *args, **options):
        days = options['days']
        cutoff = timezone.now() - timedelta(days=days)
        qs = AccessCode.objects.filter(Q(is_used=True) | Q(expires_at__lt=timezone.now()))
        to_delete = qs.filter(created_at__lt=cutoff)
        count = to_delete.count()
        if count:
            to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} access code(s) older than {days} days.'))
