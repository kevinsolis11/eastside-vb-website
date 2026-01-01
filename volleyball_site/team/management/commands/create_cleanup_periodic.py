from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a daily django-celery-beat PeriodicTask to run cleanup_accesscodes_task'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Pass this to task args (days)')

    def handle(self, *args, **options):
        days = options['days']
        try:
            from django_celery_beat.models import IntervalSchedule, PeriodicTask
            import json

            schedule, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
            pt, created = PeriodicTask.objects.get_or_create(
                name='cleanup_accesscodes_daily',
                defaults={
                    'interval': schedule,
                    'task': 'team.tasks.cleanup_accesscodes_task',
                    'args': json.dumps([days]),
                    'enabled': True,
                }
            )
            if not created:
                pt.interval = schedule
                pt.args = json.dumps([days])
                pt.enabled = True
                pt.save()

            self.stdout.write(self.style.SUCCESS('Created or updated cleanup_accesscodes_daily'))
        except Exception as e:
            self.stderr.write('Failed to create periodic task: %s' % (e,))