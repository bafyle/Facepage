from django.apps import AppConfig

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'

    def ready(self) -> None:
        from .signals import (
            delete_post_photo, update_post_counters, 
            create_post_signal, compress_image,
            notification_alarm_sse_signal, new_notification_alarm_sse
        )
        notification_alarm_sse_signal.connect(
            receiver=new_notification_alarm_sse,
            weak=True
        )
