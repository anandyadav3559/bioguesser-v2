from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import User

class Command(BaseCommand):
    help = 'Deletes guest users who have been inactive for more than 2 hours'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(hours=2)
        
        # Find stale guests
        stale_guests = User.objects.filter(
            is_guest=True,
            last_active_at__lt=threshold
        )
        
        count = stale_guests.count()
        
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Found {count} stale guest users. Deleting...'))
            # Delete them one by one to trigger signals (Room cleanup)
            for guest in stale_guests:
                guest.delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleaned up stale guests.'))
        else:
            self.stdout.write(self.style.NOTICE('No stale guest users found.'))
