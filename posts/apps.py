from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'

    def ready(self) -> None:
        from .signals import (
            delete_post_photo, update_post_counters, 
            create_post_signal, compress_image
        )
        from .models import Post
        create_post_signal.connect(
            receiver=compress_image,
            sender=Post
        )
