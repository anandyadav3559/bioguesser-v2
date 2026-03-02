import uuid
from django.db import models

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_provider = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    is_guest = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)

    @property
    def is_authenticated(self):
        return True

    def clean(self):
        if self.is_guest and self.auth_provider:
            raise ValidationError("Guest users cannot have an auth provider.")
        if not self.is_guest and not self.auth_provider:
            raise ValidationError("Non-guest users must have an auth provider.")

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['auth_provider'], name='idx_users_auth_provider'),
            models.Index(fields=['created_at'], name='idx_users_created_at'),
            models.Index(fields=['last_active_at'], name='idx_users_last_active'),
        ]
    def __str__(self):
        return self.username