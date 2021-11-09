from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self) -> None:
        from .signals import (
            create_send_friend_request_notification_receiver,
            create_comment_notification_receiver,
            create_like_notification_receiver,
            send_friend_request_signal,
            like_signal,
            comment_signal,
        )
        from posts.models import Like, Comment
        from django.contrib.auth import get_user_model as User

        send_friend_request_signal.connect(
            receiver=create_send_friend_request_notification_receiver,
            sender=User()
        )
        like_signal.connect(
            receiver=create_like_notification_receiver,
            sender=Like,
        )
        comment_signal.connect(
            receiver=create_comment_notification_receiver,
            sender=Comment,
        )

