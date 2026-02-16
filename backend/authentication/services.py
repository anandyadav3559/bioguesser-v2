from django.core.cache import cache

def get_user_profile_data(user):
    """
    Returns a dictionary of user data suitable for profile display.
    Handles both guest and permanent users.
    """
    if user.is_guest:
        redis_key = f"session:{user.user_id}"
        guest_data = cache.get(redis_key) or {}

        return {
            "identity_type": "guest",
            "user_id": str(user.user_id),
            "username": user.username,
            "guest_session": guest_data
        }

    return {
        "identity_type": "permanent",
        "user_id": str(user.user_id),
        "username": user.username,
        "email": user.email
    }
