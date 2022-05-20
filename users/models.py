from django.db import models
from django.contrib.auth import get_user_model as User
from django.core.validators import RegexValidator
from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .utils.constants import FIVE_MINUTES, HOUR

EGYPT_PHONE_NUMBER_REGEX = RegexValidator(r'^01[0125][0-9]{8}$', 'only valid phone numbers are required')


class Profile(models.Model):
    user = models.OneToOneField(User(), on_delete=models.CASCADE)
    link = models.SlugField(unique=True, max_length=100, null=False, blank=True)
    profile_picture = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    profile_cover = models.ImageField(default='profile_covers/default.jpg', upload_to='profile_covers')
    bio = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=50, blank=True, default='', validators=[EGYPT_PHONE_NUMBER_REGEX])
    verified = models.BooleanField(default=False)
    birthday = models.DateField(null=True)

    choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(choices=choices, max_length=1, default='M', null=True)


    def copy_new_data(self, data: dict, save: bool = True):
        self.user.first_name = data.get('first_name')
        self.user.last_name = data.get('last_name')
        self.phone_number = data.get('phone_number')
        self.gender = data.get('gender')
        self.birthday = data.get('birthday')
        self.bio = data.get('bio')
        if save:
            self.save()
            self.user.save()
    

    def name(self):
        return self.user.get_full_name()
    

    def __str__(self):
        return f"{self.user.username} Profile"


class Friend(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['side1', 'side2'], name='Unique_friendship')
        ]
    
    side1 = models.ForeignKey(User(), on_delete=models.CASCADE, related_name="Side1")
    side2 = models.ForeignKey(User(), on_delete=models.CASCADE, related_name="Side2")
    acceptance_date = models.DateField(blank=True, null=True)


    def clean(self) -> None:
        if self.acceptance_date == None:
            raise ValidationError(_("Friendship must have acceptance date if it has been accepted"))
        return super().clean()
    

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


    def __str__(self):
        return f"Friendship {self.side1.username} and {self.side2.username}"


class SendEmailRequest(models.Model):
    user = models.ForeignKey(User(), on_delete=models.CASCADE, related_name="requester")
    last_request = models.DateTimeField(blank=True, null=True)


    def get_time_difference_from_now(self):
        now = timezone.localtime(timezone.now())
        time_difference = now - timezone.localtime(self.last_request)
        return time_difference.total_seconds()
    

    def is_still_soon(self) -> bool:
        if (x := self.get_time_difference_from_now()) > 0 and x < FIVE_MINUTES:
            return True
        return False


class FriendRequest(models.Model):
    FRIEND_REQUEST_ACCEPTED = 1
    FRIEND_REQUEST_DECLINED = 2
    FRIEND_REQUEST_WAITING = 3
    STATUS_CHOICES = (
        (FRIEND_REQUEST_ACCEPTED, "accepted"),
        (FRIEND_REQUEST_DECLINED, "declined"),
        (FRIEND_REQUEST_WAITING, "waiting"),
    )
    user_from = models.ForeignKey(User(), on_delete=models.CASCADE, related_name="request_from")
    user_to = models.ForeignKey(User(), on_delete=models.CASCADE, related_name="request_to")
    created = models.DateTimeField(default=timezone.now, null=False, blank=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=3)

    def accept_friend_request(self):
        new_relation = Friend(side1=self.user_from, side2=self.user_to, acceptance_date=timezone.localtime(timezone.now()))
        new_relation.save()
        self.status = self.FRIEND_REQUEST_ACCEPTED
        self.save()
    
    def decline_friend_request(self):
        self.status = self.FRIEND_REQUEST_DECLINED
        self.save()

class NewAccountActivationLink(models.Model):
    user = models.ForeignKey(User(), on_delete=models.CASCADE)
    link = models.CharField(max_length=100, null=False, blank=False, unique=True)
    create_date = models.DateTimeField(null=False, blank=False, default=timezone.now)


    def expired(self) -> bool:
        now = timezone.localtime(timezone.now())
        if (now - timezone.localtime(self.create_date)).total_seconds() > HOUR:
            return True
        return False
