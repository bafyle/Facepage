from django.core import validators
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinLengthValidator

# Create your models here.

MESSAGE_MINIMUM_LEGNTH_VALIDATOR = MinLengthValidator(1)

class Message(models.Model):
    message_content = models.TextField(blank=False, null=False, validators=[MESSAGE_MINIMUM_LEGNTH_VALIDATOR])
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sender', null=True)
    receiver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='receiver', null=True)
    send_date = models.DateTimeField(default=timezone.now)
    seen = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Message sent on: {self.send_date} from: {self.sender} to: {self.receiver}"