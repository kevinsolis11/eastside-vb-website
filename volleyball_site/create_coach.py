#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volleyball_site.settings')
django.setup()

from django.contrib.auth.models import User

# Check if coach already exists
if User.objects.filter(username='coach_test').exists():
    print('Coach account already exists')
    coach = User.objects.get(username='coach_test')
else:
    coach = User.objects.create_user(
        username='coach_test',
        email='coach@test.com',
        password='Coach123Pass',
        first_name='Coach',
        last_name='Test',
        is_staff=True
    )
    print('✅ Coach account created!')

print(f'\n📋 Test Coach Account Credentials:')
print(f'   Username: coach_test')
print(f'   Email: coach@test.com')
print(f'   Password: Coach123Pass')
print(f'   Staff Status: {coach.is_staff}')
