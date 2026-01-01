#!/bin/bash
# Create test admin account

cd volleyball_site
python manage.py shell << END
from django.contrib.auth.models import User

# Create test account
if not User.objects.filter(username='testadmin').exists():
    User.objects.create_superuser('testadmin', 'test@example.com', 'testpass123')
    print('✅ Test admin created:')
    print('   Username: testadmin')
    print('   Password: testpass123')
    print('   Email: test@example.com')
else:
    print('⚠️ Test admin already exists')
    
# List all superusers
print('\nAll admin accounts:')
for user in User.objects.filter(is_superuser=True):
    print(f'   - {user.username} ({user.email})')
END
