import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from apps.users.models import User
u = User.objects.get(username='admin')
u.role = 'admin'
u.save()
print('Done:', u.username, u.role)
