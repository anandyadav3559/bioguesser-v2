from django.core.cache import cache
from game.models import Player, Guess
from userprofile.models import UserProfile

def get_user_profile_data(user):
    """
    Returns a dictionary of user data suitable for profile display.
    Handles both guest and permanent users.
    """
    
    # 1. Fetch Profile Stats
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
            "total_score": 0,
            "high_score": 0
        }

    # 2. Fetch Recent Game History
    # We look up Player records associated with this user, ordered by most recently joined
    recent_players = Player.objects.filter(user=user).select_related('room').order_by('-joined_at')[:10]
    
    history = []
    for p in recent_players:
        # Get all their guesses for this room
        guesses = Guess.objects.filter(player=p).select_related('round__animal').order_by('round__round_number')
        
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

    return base_data
