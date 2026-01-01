from django.apps import AppConfig


class TeamConfig(AppConfig):
    name = 'team'
    verbose_name = 'Team'
    # Intentionally no DB access in ready(); use management command to install periodic tasks.
