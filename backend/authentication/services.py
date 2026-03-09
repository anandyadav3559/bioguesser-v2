from django.core.cache import cache
from game.models import Player, Guess
from userprofile.models import UserProfile

def get_profile_cache_key(user_id):
    return f"profile:{user_id}"

def get_full_profile_cache_key(user_id):
    return f"profile_full:{user_id}"

def refresh_user_profile_cache(user):
    """
    Reads the UserProfile from the database and writes its stats to a Redis hash.
    Also ensures the profile is tracked in the dirty set for eventual sync.
    """
    try:
        profile = user.profile
        stats = {
            "games_played": profile.games_played,
            "total_score": profile.total_score,
            "high_score": profile.high_score
        }
    except UserProfile.DoesNotExist:
        stats = {
            "games_played": 0,
            "total_score": 0.0,
            "high_score": 0.0
        }
    
    # Write to Redis Hash
    cache_key = get_profile_cache_key(user.user_id)
    cache.set(cache_key, stats, timeout=2592000) # 30 days
    return stats


def get_user_profile_data(user):
    """
    Returns a dictionary of user data suitable for profile display.
    Handles both guest and permanent users.
    Reads statistics from Redis caching layer first.
    """
    full_cache_key = get_full_profile_cache_key(user.user_id)
    cached_full_profile = cache.get(full_cache_key)
    if cached_full_profile:
        return cached_full_profile
    
    # 1. Fetch Profile Stats from Redis
    cache_key = get_profile_cache_key(user.user_id)
    stats = cache.get(cache_key)
    
    # Cache miss (e.g., redis restarted, or first API call before cache warm)
    if stats is None:
        stats = refresh_user_profile_cache(user)
    # stats is now populated either from Redis or DB fallback
    # Convert numerical strings back to floats/ints if they came from Redis string hash
    stats = {
        "games_played": int(stats.get("games_played", 0)),
        "total_score": float(stats.get("total_score", 0.0)),
        "high_score": float(stats.get("high_score", 0.0))
    }

    from django.db.models import Prefetch

    # 2. Fetch Recent Game History
    # We look up Player records associated with this user, ordered by most recently joined,
    # and prefetch all necessary related objects to avoid N+1 query problems.
    recent_players = Player.objects.filter(user=user).select_related(
        'room'
    ).prefetch_related(
        Prefetch(
            'guesses',
            queryset=Guess.objects.select_related('round__animal').order_by('round__round_number')
        )
    ).order_by('-joined_at')[:10]
    
    history = []
    for p in recent_players:
        # iterate over prefetched guesses
        guesses = p.guesses.all()
        
        rounds_data = []
        for g in guesses:
            animal = g.round.animal
            if animal:
                rounds_data.append({
                    "round_number": g.round.round_number,
                    "score_awarded": g.score_awarded,
                    "animal": {
                        "id": animal.id,
                        "common_name": animal.name,
                        "scientific_name": animal.scientific_name,
                        "image_url": animal.image_url
                    }
                })

        history.append({
            "room_code": p.room.room_code,
            "status": p.room.status,
            "played_at": p.joined_at.isoformat(),
            "total_score": p.score,
            "rounds": rounds_data
        })


    base_data = {
        "user_id": str(user.user_id),
        "username": user.username,
        "stats": stats,
        "history": history
    }

    if user.is_guest:
        redis_key = f"session:{user.user_id}"
        guest_data = cache.get(redis_key) or {}
        base_data.update({
            "identity_type": "guest",
            "guest_session": guest_data
        })
    else:
        base_data.update({
            "identity_type": "permanent",
            "email": user.email
        })

    cache.set(full_cache_key, base_data, timeout=2592000) # 30 days
    return base_data
