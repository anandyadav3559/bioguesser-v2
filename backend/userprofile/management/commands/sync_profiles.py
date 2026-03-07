import time
from django.core.management.base import BaseCommand
from django.core.cache import cache
from userprofile.models import UserProfile
from authentication.services import get_profile_cache_key

class Command(BaseCommand):
    help = 'Syncs dirty UserProfile data from Redis cache back to the PostgreSQL database.'

    def handle(self, *args, **options):
        self.stdout.write("Starting Redis -> DB Profile Sync...")
        start_time = time.time()

        # Pop all currently dirty user IDs
        # We use a pipeline to handle atomic popping if needed, but since it's a scheduled job,
        # SMEMBERS + DEL is safe enough if we assume this is the only sync worker.
        client = cache.client.get_client()
        dirty_user_ids = client.smembers("profiles:dirty")
        
        if not dirty_user_ids:
            self.stdout.write(self.style.SUCCESS("No dirty profiles found. Sync complete."))
            return

        # Decode byte strings
        dirty_user_ids = [uid.decode('utf-8') for uid in dirty_user_ids]
        
        # Clear the set so any new games played *during* this sync go into a fresh set
        client.delete("profiles:dirty")

        # Fetch the actual profile objects from DB
        profiles_to_update = list(UserProfile.objects.filter(user_id__in=dirty_user_ids))
        profile_map = {str(p.user_id): p for p in profiles_to_update}

        updates_made = 0
        for uid in dirty_user_ids:
            cache_key = get_profile_cache_key(uid)
            stats = cache.get(cache_key)

            if stats and uid in profile_map:
                profile = profile_map[uid]
                profile.games_played = int(stats.get("games_played", profile.games_played))
                profile.total_score = float(stats.get("total_score", profile.total_score))
                profile.high_score = float(stats.get("high_score", profile.high_score))
                updates_made += 1

        if updates_made > 0:
            UserProfile.objects.bulk_update(
                profiles_to_update,
                ['games_played', 'total_score', 'high_score']
            )

        elapsed = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(
            f"Successfully synced {updates_made} profiles in {elapsed:.2f}s."
        ))
