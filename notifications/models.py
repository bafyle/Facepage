from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Notification(models.Model):
    user_from = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='notification_from')
    user_to = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name='notification_to', null=True)
    content = models.CharField(max_length=200, blank=False, null=False, )
    choices = [('C', 'Comment'), ('L', 'Like'), ('F', 'Friend'), ]
    type = models.CharField(choices=choices, max_length=1, null=False, blank=False,)
    picture = models.ImageField(default='profile_pics/default.jpg')

    def __str__(self):
        return f"{self.user_to} notification"