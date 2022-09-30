from django.urls import re_path
from .consumers import ChatWebsocket



"""
Routing for the WebSockets for the chat feature

"""
websockets_urlpattern = [
    re_path(r"chat/(?P<pk>\w+)/$", ChatWebsocket.as_asgi()),
]