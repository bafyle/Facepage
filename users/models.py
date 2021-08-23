from django.db import models
from django.contrib.auth import get_user_model as User

class Profile(models.Model):
    user = models.OneToOneField(User(), on_delete=models.CASCADE)
    link = models.SlugField(unique=True, max_length=100, null=False, blank=True)
    profile_picture = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    profile_cover = models.ImageField(default='profile_covers/default.jpg', upload_to='profile_covers')
    bio = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=50, blank=True, default='')
    verified = models.BooleanField(default=False)
    birthday = models.DateField(null=True)

    choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(choices=choices, max_length=1, default='M', null=True)

    def name(self):
        return self.user.get_full_name()
    
    def __str__(self):
        return f"{self.user.username} Profile"


class Friend(models.Model):
    class Meta:
        unique_together = (('side1', 'side2'), )
        
    side1 = models.ForeignKey(User(), on_delete=models.CASCADE, related_name="Side1")
    side2 = models.ForeignKey(User(), on_delete=models.CASCADE, related_name="Side2")
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Friendship {self.side1.username} and {self.side2.username}"
