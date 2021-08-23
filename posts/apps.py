from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'

    def ready(self) -> None:
        from .signals import deletePhotoFromServer
        return super().ready()
