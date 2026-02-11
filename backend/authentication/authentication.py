# authentication/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.core.cache import cache
from .models import User


class CustomJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")

        if not user_id:
            raise AuthenticationFailed("Token missing user_id")

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        # OPTIONAL: Redis session validation
        redis_key = f"session:{user.user_id}"
        session_exists = cache.get(redis_key)

        if not session_exists:
            raise AuthenticationFailed("Session expired or invalid")

        return user
