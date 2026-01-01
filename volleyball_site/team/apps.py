from django.apps import AppConfig


class TeamConfig(AppConfig):
    name = 'team'
    verbose_name = 'Team'
    
    def ready(self):
        """Register signal handlers and startup checks when app is ready."""
        import team.signals  # noqa
        import team.checks  # noqa
