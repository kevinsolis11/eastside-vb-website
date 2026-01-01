# Generated migration to create admin account

from django.db import migrations
from django.contrib.auth.models import User


def create_admin(apps, schema_editor):
    """Create admin user if it doesn't exist"""
    if not User.objects.filter(username='kevinsolis').exists():
        User.objects.create_superuser(
            username='kevinsolis',
            email='kevinsolis@example.com',
            password='admin123'
        )
        print('✅ Admin account created: kevinsolis / admin123')
    else:
        # Update password to ensure it's correct
        user = User.objects.get(username='kevinsolis')
        user.set_password('admin123')
        user.save()
        print('✅ Admin account verified')


def reverse_create_admin(apps, schema_editor):
    """Remove admin user"""
    User.objects.filter(username='kevinsolis').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0009_videoanalysis'),
    ]

    operations = [
        migrations.RunPython(create_admin, reverse_create_admin),
    ]
