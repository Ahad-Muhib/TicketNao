import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelbooker.settings')
django.setup()

from django.contrib.auth.models import User

# Check if a superuser already exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' has been created with password 'admin123'")
else:
    print("Superuser 'admin' already exists")