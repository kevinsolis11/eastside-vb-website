# Generated migration to create admin account

from django.db import migrations
from django.contrib.auth.models import User


def create_admin_user(apps, schema_editor):
    """Create admin user if it doesn't exist"""
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='kevinsolis').exists():
        User.objects.create_superuser(
            username='kevinsolis',
            email='kevinsolis@example.com',
            password='admin123'
        )


def reverse_admin_user(apps, schema_editor):
    """Remove admin user"""
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='kevinsolis').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0009_videoanalysis'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, reverse_admin_user),
    ]
