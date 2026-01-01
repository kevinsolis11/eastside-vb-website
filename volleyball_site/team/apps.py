from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_admin_user(sender, **kwargs):
    """Create admin user after migrations"""
    import os
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        from django.contrib.auth.models import User
        if not User.objects.filter(username='kevinsolis').exists():
            User.objects.create_superuser('kevinsolis', 'kevinsolis@example.com', 'admin123')


class TeamConfig(AppConfig):
    name = 'team'
    verbose_name = 'Team'
    
    def ready(self):
        """Register signal handlers"""
        post_migrate.connect(create_admin_user, sender=self)
