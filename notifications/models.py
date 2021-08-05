from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.


class Notification(models.Model):
    class Meta:
        unique_together = (('route_id', 'type', 'user_from'), )

    user_from = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='notification_from')
    user_to = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name='notification_to', null=True)
    content = models.CharField(max_length=200, blank=False, null=False, )
    
    choices = [('C', 'Comment'), ('L', 'Like'), ('F', 'Friend'), ]
    type = models.CharField(choices=choices, max_length=1, null=False, blank=False,)
    picture = models.ImageField(default='profile_pics/default.jpg')
    date = models.DateTimeField(auto_now_add=True)
    route_id = models.SlugField(default=None)
    seen = models.BooleanField(default=False)

    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user_to} notification"