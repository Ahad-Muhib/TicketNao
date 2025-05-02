import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelbooker.settings')
django.setup()

from django.contrib.auth.models import User

# Check if admin exists
admin = User.objects.filter(username='admin').first()
if admin:
    # Make sure admin is a superuser
    if not admin.is_superuser:
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        print(f"Updated {admin.username} to be a superuser")
    else:
        print(f"Admin user {admin.username} is already a superuser")
else:
    # Create a new admin superuser
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Created new admin superuser with username 'admin' and password 'admin123'")