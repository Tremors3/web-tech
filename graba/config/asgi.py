"""
ASGI config for config project.
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

## Developement Configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.django.local')

## Production Configuration
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.django.produ')

import auctions.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(auctions.routing.websocket_urlpatterns)
    ),
})
