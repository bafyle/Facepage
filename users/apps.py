from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self) -> None:
        from .signals import (
            delete_profile_pictures_receiver,
            account_register_receiver
        )

