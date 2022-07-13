from multiprocessing.sharedctypes import Value
from re import I
from django.db.models.signals import post_delete, post_save
from django.dispatch import Signal
from django.conf import settings
import os
from django.dispatch.dispatcher import receiver
from .models import Post, Comment, Like
from PIL import Image

from .utils import image_resize, save_compressed_image

create_post_signal = Signal()

@receiver(post_delete, sender=Post)
def delete_post_photo(instance, **kwargs):
    instance.image.delete(False)

@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Like)
@receiver(post_delete, sender=Comment)
@receiver(post_delete, sender=Like)
def update_post_counters(instance, **kwargs):
    instance.post.likes = Like.objects.filter(post=instance.post).count()
    instance.post.comments = Comment.objects.filter(post=instance.post).count()
    instance.post.save()


def compress_image(instance, **kwargs):
    try:
        instance.image.open()
    except ValueError as e:
        return
    image_path = os.path.join(settings.MEDIA_ROOT, instance.image.__str__())
    image = Image.open(instance.image)
    image_resize(image)
    save_compressed_image(image, image_path)

