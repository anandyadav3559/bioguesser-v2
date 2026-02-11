# authentication/admin.py
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'auth_provider', 'is_guest', 'created_at')
    list_filter = ('auth_provider', 'is_guest')
