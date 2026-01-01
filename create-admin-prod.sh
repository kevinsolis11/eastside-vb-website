#!/bin/bash
# One-time setup script to create admin user in production

cd volleyball_site
python manage.py shell << 'EOF'
from django.contrib.auth.models import User

if not User.objects.filter(username='kevinsolis').exists():
    User.objects.create_superuser('kevinsolis', 'kevinsolis@example.com', 'admin123')
    print('✅ Admin created: kevinsolis / admin123')
else:
    print('ℹ️ Admin already exists')
EOF
