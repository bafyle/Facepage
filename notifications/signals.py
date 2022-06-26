from django.dispatch import Signal
from .models import Notification

like_signal = Signal()
comment_signal = Signal()
send_friend_request_signal = Signal()

def create_like_notification_receiver(**kwargs):
    
    Notification.objects.create(
        user_from=kwargs.get("user_from"),
        user_to=kwargs.get("user_to"),
        content=kwargs.get("content"),
        type='L',
        picture=kwargs.get("picture"),
        content_object=kwargs.get("content_object"),
        route_id=kwargs.get("route_id")
    )

def create_comment_notification_receiver(**kwargs):

    Notification.objects.create(
        route_id=kwargs.get("route_id"),
        user_from=kwargs.get("user_from"),
        type='C',
        user_to=kwargs.get("user_to"),
        content=kwargs.get("content"),
        picture=kwargs.get("picture"),
        content_object=kwargs.get("content_object"),
    )

def create_send_friend_request_notification_receiver(**kwargs):
    Notification.objects.create(
        user_from=kwargs.get("user_from"),
        user_to=kwargs.get("user_to"),
        content=kwargs.get("content"),
        type='F',
        picture=kwargs.get("picture"),
        content_object=kwargs.get("content_object"),
        route_id=kwargs.get("route_id")
    )

