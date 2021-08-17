from django.apps import AppConfig

class PostsConfig(AppConfig):
    name = 'posts'

    def ready(self) -> None:
        from .signals import deletePhotoFromServer
        return super().ready()
