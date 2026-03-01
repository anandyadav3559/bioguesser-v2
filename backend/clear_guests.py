import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import User
from django.core.cache import cache

def clear_guest__data():
    guests = User.objects.filter(is_guest=True)
    count = 0
    for guest in guests:
        cache.delete(f"session:{guest.user_id}")
        count += 1
    
    deleted_count, _ = guests.delete()
    print(f"Deleted {count} guest sessions from Redis.")
    print(f"Deleted {deleted_count} guest users from Database.")

if __name__ == '__main__':
    clear_guest_data()
