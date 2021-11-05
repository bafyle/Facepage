from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from .models import Profile

@receiver(post_delete, sender=Profile)
def delete_profile_pictures_receiver(instance, **kwargs):
    if instance.profile_picture.url.split('/')[-1] != 'default.jpg':
        instance.profile_picture.delete(False)
    if instance.profile_cover.url.split('/')[-1] != 'default.jpg':
        instance.profile_cover.delete(False)