"""
ASGI config for EduGrade AI project with Channels & ReactPy WebSocket support.
"""

import os
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edugrade.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from reactpy_django import REACTPY_WEBSOCKET_ROUTE

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            REACTPY_WEBSOCKET_ROUTE,
        ])
    ),
})
