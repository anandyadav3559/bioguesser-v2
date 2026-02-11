# authentication/urls.py
from django.urls import path
from .views import (
    UserListView,
    PermanentUserCreateView,
    GuestAuthView,
    MeView,
    LogoutView,
    GoogleAuthView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Original / Users
    path('users/', UserListView.as_view()),
    path('permanent/',PermanentUserCreateView.as_view()),
    
    # Guest + Identity (Added by user)
    path("guest/", GuestAuthView.as_view(), name="guest"),
    path("me/", MeView.as_view(), name="me"), # Replaces 'get_current_user' based on user's diff
    path("google/", GoogleAuthView.as_view(), name="google-login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # JWT
    path("login/", TokenObtainPairView.as_view(), name="jwt-login"), # Updated name per user request
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"), # Updated name per user request
]
