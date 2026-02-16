# authentication/views.py

import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication
from .authentication import CustomJWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.core.cache import cache
from .models import User
from .serializers import UserSerializer
from .services import get_user_profile_data


class UserListView(APIView):
    authentication_classes = [SessionAuthentication, CustomJWTAuthentication]
    permission_classes = [IsAdminUser]
    
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
        cache.set(redis_key, {"active": True}, timeout=2592000)

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
        cache.set(redis_key, {"active": True}, timeout=2592000)

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

        profile_data = get_user_profile_data(user)
        return Response(profile_data)


# -------------------------
# Logout (Revocation)
# -------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        redis_key = f"session:{request.user.user_id}"
        cache.delete(redis_key)

        return Response({"message": "Logged out successfully"})


# -------------------------
# Google Auth
# -------------------------
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify token
            id_info = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                # audience=os.getenv("GOOGLE_CLIENT_ID") 
            )

            email = id_info.get("email")
            if not email:
                return Response({"error": "Invalid token: Email not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Get or Create User
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"user_{uuid.uuid4().hex[:8]}",
                    "auth_provider": "google",
                    "is_guest": False
                }
            )

            # Update auth_provider if existing user didn't have one
            if not created and not user.auth_provider:
                user.auth_provider = "google"
                user.save()

            # Create Session
            redis_key = f"session:{user.user_id}"
            cache.set(redis_key, {"active": True}, timeout=2592000) # 30 days

            # Generate JWT
            access_token = AccessToken()
            access_token["user_id"] = str(user.user_id)
            access_token["identity_type"] = "permanent"

            return Response({
                "access": str(access_token),
                "user_id": str(user.user_id),
                "identity_type": "permanent",
                "email": user.email,
                "created": created
            })

        except ValueError as e:
            return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
