from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0005_accesscode_allowed_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesscode',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
