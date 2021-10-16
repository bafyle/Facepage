from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from .models import Post

@receiver(post_delete, sender=Post)
def delete_post_photo(instance, **kwargs):
    instance.image.delete(False)
    