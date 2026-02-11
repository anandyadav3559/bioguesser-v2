# authentication/views.py

import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from django.core.cache import cache
from .models import User
from .serializers import UserSerializer


class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)


# -------------------------
# Guest Login
# -------------------------
class GuestAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 1️⃣ Create DB guest user
        user = User.objects.create(
            username=f"guest_{uuid.uuid4().hex[:8]}",
            is_guest=True,
            auth_provider="guest"
        )

        # 2️⃣ Store session in Redis (1 hour TTL)
        redis_key = f"session:{user.user_id}"
        cache.set(redis_key, {"active": True}, timeout=3600)

        # 3️⃣ Create JWT
        token = AccessToken()
        token["user_id"] = str(user.user_id)
        token["identity_type"] = "guest"

        return Response({
            "access": str(token),
            "user_id": str(user.user_id),
            "identity_type": "guest"
        }, status=status.HTTP_201_CREATED)


# -------------------------
# Permanent User Creation (Mock for now)
# -------------------------
class PermanentUserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = User.objects.create(
            username=f"user_{uuid.uuid4().hex[:8]}",
            email=request.data.get("email"),
            auth_provider="manual",
            is_guest=False
        )

        redis_key = f"session:{user.user_id}"
        cache.set(redis_key, {"active": True}, timeout=3600)

        token = AccessToken()
        token["user_id"] = str(user.user_id)
        token["identity_type"] = "permanent"

        return Response({
            "access": str(token),
            "user_id": str(user.user_id),
            "identity_type": "permanent"
        }, status=status.HTTP_201_CREATED)


# -------------------------
# /me Endpoint
# -------------------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_guest:
            redis_key = f"session:{user.user_id}"
            guest_data = cache.get(redis_key) or {}

            return Response({
                "identity_type": "guest",
                "user_id": str(user.user_id),
                "username": user.username,
                "guest_session": guest_data
            })

        return Response({
            "identity_type": "permanent",
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email
        })


# -------------------------
# Logout (Revocation)
# -------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        redis_key = f"session:{request.user.user_id}"
        cache.delete(redis_key)

        return Response({"message": "Logged out successfully"})
