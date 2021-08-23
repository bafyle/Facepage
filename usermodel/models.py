from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(verbose_name=_("email address"), unique=True)

    def get_full_name(self) -> str:
        return super().get_full_name()
    
    def get_short_name(self) -> str:
        return super().get_short_name()
