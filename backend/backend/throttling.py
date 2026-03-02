"""
Project-level throttle classes.

All rate-limit definitions live here — single source of truth.
Rates are configured in settings.DEFAULT_THROTTLE_RATES, keyed by `scope`.
"""
from rest_framework.throttling import SimpleRateThrottle


class UsernameLoginThrottle(SimpleRateThrottle):
    """Email-based account creation — keyed by email address."""
    scope = 'user_login'

    def get_cache_key(self, request, view):
        ident = request.data.get('email')
        if not ident:
            return None
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class GuestLoginThrottle(SimpleRateThrottle):
    """
    /auth/guest/ — keyed by client IP.
    Each call creates a real DB user + Redis session; must be tightly bounded.
    """
    scope = 'guest_login'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class GoogleLoginThrottle(SimpleRateThrottle):
    """
    /auth/google/ — keyed by client IP.
    Prevents token-stuffing and Google API enumeration attacks.
    """
    scope = 'google_login'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class GuessSubmitThrottle(SimpleRateThrottle):
    """
    /game/guess/ — keyed by authenticated user ID.
    Guards the evaluate_round() DB transaction from rapid-fire calls.
    """
    scope = 'guess_submit'

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': str(request.user.pk),
        }


class RoundStartThrottle(SimpleRateThrottle):
    """
    /game/start_round/ — keyed by authenticated user ID.
    Generous enough for normal gameplay; prevents runaway round-creation loops.
    """
    scope = 'round_start'

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': str(request.user.pk),
        }
