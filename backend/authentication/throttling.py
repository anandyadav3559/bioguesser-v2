from rest_framework.throttling import SimpleRateThrottle

class UsernameLoginThrottle(SimpleRateThrottle):
    scope = 'user_login'

    def get_cache_key(self, request, view):
        # Check for 'email' because our PermanentUserCreateView uses it.
        # Guest login has no input, so we return None (not throttled by this class).
        ident = request.data.get('email')
        if not ident:
            return None
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
