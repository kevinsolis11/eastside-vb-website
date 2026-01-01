from django.apps import AppConfig


class TeamConfig(AppConfig):
    name = 'team'
    verbose_name = 'Team'
    
    def ready(self):
        """Register signal handlers when app is ready."""
        import team.signals  # noqa
