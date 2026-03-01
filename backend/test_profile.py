import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import User
from authentication.services import get_user_profile_data

user = User.objects.first()
print(get_user_profile_data(user))
