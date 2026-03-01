import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import User
from authentication.services import get_user_profile_data

print("Finding guest user...")
guest = User.objects.filter(is_guest=True).first()
if guest:
    try:
        print("Calling get_user_profile_data...")
        data = get_user_profile_data(guest)
        print("Success!", data)
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("No guest user found.")
