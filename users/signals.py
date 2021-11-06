from io import StringIO
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver, Signal
from .models import NewAccountActivationLink, Profile
from django.contrib.auth import get_user_model as User

create_profile_signal = Signal()
create_activation_link_signal = Signal()

@receiver(post_delete, sender=Profile)
def delete_profile_pictures_receiver(instance, **kwargs):
    if instance.profile_picture.url.split('/')[-1] != 'default.jpg':
        instance.profile_picture.delete(False)
    if instance.profile_cover.url.split('/')[-1] != 'default.jpg':
        instance.profile_cover.delete(False)

@receiver(create_profile_signal, sender=User())
def account_register_receiver(user, gender, link, birthday, **kwargs):
    Profile.objects.create(
        user=user,
        gender=gender,
        link=link,
        birthday=birthday
    )

@receiver(create_activation_link_signal, sender=User())
def create_activation_link_receiver(user, activation_link, **kwargs):
    NewAccountActivationLink.objects.create(user=user, link=activation_link)