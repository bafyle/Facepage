"""
ASGI config for facepage project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from messenger.routing import websockets_urlpattern
from django.urls import path, re_path
import django_eventstream
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facepage.settings')


application = ProtocolTypeRouter(
    {
        """
        http protocol request will be splitted to two
        one for regular http requests and one for pushing SSE
        """
        'http': URLRouter([
            path('events/<link>/',
                AuthMiddlewareStack(
                    URLRouter(django_eventstream.routing.urlpatterns)
                    ), { 'format-channels': ['event-stream-{link}'] }
            ),
            re_path(r'', get_asgi_application()),
        ]),
        "websocket": AuthMiddlewareStack(
            URLRouter(websockets_urlpattern)
        ),
    })
