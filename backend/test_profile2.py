import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import User
from authentication.services import get_user_profile_data

guest = User.objects.filter(is_guest=True).first()
if guest:
    try:
        print(get_user_profile_data(guest))
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("No guest")
