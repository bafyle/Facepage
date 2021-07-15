from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    profile_cover = models.ImageField(default='profile_covers/default_cover.jpg', upload_to='profile_covers')
    bio = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=50, blank=True, default='')
    verified = models.BooleanField(default=False)
    birthday = models.DateField(null=True)

    choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(choices=choices, max_length=1, default='M', null=True)

    def __str__(self):
        return f"{self.user.username} Profile"