from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from .models import Post, Comment, Like

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
