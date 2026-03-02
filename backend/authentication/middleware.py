from django.utils import timezone
from .models import User

class UpdateLastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # After the response is ready, update the timestamp if user is authenticated
        if request.user.is_authenticated:
            # We use update() to avoid triggering signals or updating other fields
            User.objects.filter(user_id=request.user.user_id).update(last_active_at=timezone.now())
        
        return response
