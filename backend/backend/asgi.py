"""
ASGI config for backend project.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.asgi import get_asgi_application

# Must call get_asgi_application() FIRST — it calls django.setup() internally,
# which initialises the app registry. Importing consumers before this causes
# AppRegistryNotReady because simplejwt tries to access Django models at import time.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import multiplayer.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            multiplayer.routing.websocket_urlpatterns
        )
    ),
})
